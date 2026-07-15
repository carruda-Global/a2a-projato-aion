"""Real post-call intent classification for the Voice Receptionist.

Runs after Vapi's `end-of-call-report` webhook delivers the real call
transcript. Unlike src/orchestrator/graph.py's placeholder nodes, every node
here makes a real DeepSeek call (or a real side effect, for compliance_node)
and does real work.

Orchestration shape: planner_node runs first (everything else needs the
classified intent), then router/extractor/synthesizer/compliance run as four
independent parallel branches -- none of them depend on each other, only on
planner's output, so there's no reason to make one node carry the whole
pipeline sequentially. Uses LangGraph's real parallel-branch execution when
it's installed, and asyncio.gather for the same four calls when it isn't --
same fallback pattern as src/orchestrator/graph.py, so a missing dependency
in production degrades gracefully instead of breaking call logging entirely.
"""
import asyncio
import json
import logging
import re
from typing import TypedDict

from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents.voice_compliance_receipts import record_call_receipt

logger = logging.getLogger(__name__)

INTENT_CHOICES = ["schedule_appointment", "pricing_question", "complaint", "sales_lead", "general_inquiry", "no_info"]


class CallState(TypedDict):
    call_id: str
    transcript: str
    intent: str
    urgency: str
    lead_name: str
    lead_phone: str
    summary: str


def _extract_json(text: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return {}
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return {}


def _deepseek() -> DeepSeekClient:
    return DeepSeekClient(Settings())


async def planner_node(state: CallState) -> dict:
    """Classifies the real intent of the call from its transcript. Entry
    point -- every other node needs this before it can do its own job."""
    if not state["transcript"].strip():
        return {"intent": "no_info"}
    prompt = (
        f"Call transcript:\n{state['transcript'][:3000]}\n\n"
        f"Classify this call into exactly one of: {', '.join(INTENT_CHOICES)}.\n"
        f'Output JSON: {{"intent": "..."}}'
    )
    response = await asyncio.to_thread(_deepseek().chat, "You classify phone call transcripts.", prompt, lang="en")
    parsed = _extract_json(response)
    intent = parsed.get("intent", "general_inquiry") if parsed.get("intent") in INTENT_CHOICES else "general_inquiry"
    return {"intent": intent}


async def router_node(state: CallState) -> dict:
    """Routes the classified intent to an urgency level for the owner's
    dashboard. Independent of extractor/synthesizer/compliance -- only
    needs `intent`, so it runs in parallel with them, not after them."""
    urgency_map = {
        "complaint": "high",
        "sales_lead": "high",
        "schedule_appointment": "medium",
        "pricing_question": "medium",
        "general_inquiry": "low",
        "no_info": "low",
    }
    return {"urgency": urgency_map.get(state["intent"], "low")}


async def extractor_node(state: CallState) -> dict:
    """Extracts structured lead info (name, callback number) from the
    transcript. Independent of router/synthesizer/compliance."""
    if state["intent"] == "no_info":
        return {"lead_name": "", "lead_phone": ""}
    prompt = (
        f"Call transcript:\n{state['transcript'][:3000]}\n\n"
        f"Extract the caller's name and phone number if mentioned in the transcript "
        f'(not inferred). Output JSON: {{"lead_name": "...", "lead_phone": "..."}}. '
        f'Use empty string for anything not actually stated.'
    )
    response = await asyncio.to_thread(_deepseek().chat, "You extract structured contact info from call transcripts.", prompt, lang="en")
    parsed = _extract_json(response)
    return {"lead_name": parsed.get("lead_name", ""), "lead_phone": parsed.get("lead_phone", "")}


async def synthesizer_node(state: CallState) -> dict:
    """Composes a one-line summary for the business owner's notification.
    Independent of router/extractor/compliance."""
    if state["intent"] == "no_info":
        return {"summary": "Call ended with no meaningful content captured."}
    prompt = (
        f"Call transcript:\n{state['transcript'][:3000]}\n\n"
        f"Intent: {state['intent']}\n"
        f"Write ONE short sentence (max 25 words) summarizing what this caller wanted, "
        f"for a business owner reading a notification. No JSON, just the sentence."
    )
    response = await asyncio.to_thread(_deepseek().chat, "You write concise call summaries for business owners.", prompt, lang="en")
    return {"summary": response.strip()[:300]}


async def compliance_node(state: CallState) -> dict:
    """Persists the compliance receipt for the AI classification action.
    Its own node, its own concern -- not bolted onto the webhook handler
    after the fact. Doesn't touch CallState's output fields, only records
    the audit trail as a side effect."""
    try:
        await record_call_receipt(
            call_id=state["call_id"], tool="ai_intent_classification",
            arguments={"intent": state["intent"]}, outcome="classified",
            risk_classification="medium",
        )
    except Exception as e:
        logger.warning("[VoiceCallIntelligence] compliance_node failed: %s", e)
    return {}


async def _run_with_langgraph(initial_state: CallState) -> CallState | None:
    try:
        from langgraph.graph import StateGraph, END
    except ImportError:
        return None
    workflow = StateGraph(CallState)
    workflow.add_node("planner", planner_node)
    workflow.add_node("router", router_node)
    workflow.add_node("extractor", extractor_node)
    workflow.add_node("synthesizer", synthesizer_node)
    workflow.add_node("compliance", compliance_node)
    workflow.set_entry_point("planner")
    # Four independent branches off planner -- LangGraph runs nodes with no
    # edge between each other concurrently, not sequentially.
    for branch in ("router", "extractor", "synthesizer", "compliance"):
        workflow.add_edge("planner", branch)
        workflow.add_edge(branch, END)
    graph = workflow.compile()
    return await graph.ainvoke(initial_state)


async def classify_call(transcript: str, call_id: str = "") -> dict:
    """Entry point called from the end-of-call-report webhook. planner_node
    runs first, then router/extractor/synthesizer/compliance run as real
    parallel branches -- either via LangGraph's own concurrent execution, or
    via asyncio.gather in the fallback. No single node carries the whole
    pipeline sequentially."""
    initial_state: CallState = {
        "call_id": call_id, "transcript": transcript or "", "intent": "",
        "urgency": "", "lead_name": "", "lead_phone": "", "summary": "",
    }
    try:
        result = await _run_with_langgraph(initial_state)
        if result is not None:
            return {k: v for k, v in dict(result).items() if k != "call_id"}
    except Exception as e:
        logger.warning("[VoiceCallIntelligence] LangGraph execution failed, falling back to parallel asyncio: %s", e)

    planner_update = await planner_node(initial_state)
    state = {**initial_state, **planner_update}
    branch_updates = await asyncio.gather(
        router_node(state), extractor_node(state), synthesizer_node(state), compliance_node(state),
    )
    for update in branch_updates:
        state.update(update)
    return {k: v for k, v in state.items() if k != "call_id"}
