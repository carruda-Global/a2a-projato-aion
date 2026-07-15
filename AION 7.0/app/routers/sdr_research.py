"""Real research/review capability for the SDR worker, exposed over HTTP
since the SDR runs as a separate, dependency-lean Render worker (no LLM/
embedding SDKs installed there) -- same reasoning as linkedin_content.py,
different mechanism (SDR is a long-running process, not a per-request
job), so this is a real endpoint with the same admin-secret auth instead
of an in-process sys.path import."""
import logging

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.app_utils.marketplace_auth import require_marketplace_admin_secret
from src.agents.sdr_research_rag import ingest_research, retrieve_research
from src.agents.web_search_client import search_web
from src.config import Settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sdr-research", tags=["sdr_research"])


class IngestRequest(BaseModel):
    topic: str
    text: str
    source: str = ""


class QueryRequest(BaseModel):
    query: str
    k: int = 5


class CouncilRequest(BaseModel):
    proposal: str


@router.post("/ingest")
async def ingest(request: Request, body: IngestRequest):
    settings = Settings()
    require_marketplace_admin_secret(request, getattr(settings, "marketplace_admin_secret", ""))
    stored = await ingest_research(body.topic, body.text, body.source)
    return {"stored_chunks": stored}


@router.post("/query")
async def query(request: Request, body: QueryRequest):
    settings = Settings()
    require_marketplace_admin_secret(request, getattr(settings, "marketplace_admin_secret", ""))
    results = await retrieve_research(body.query, body.k)
    if results:
        return {"results": results, "source": "rag"}
    live = await search_web(body.query)
    if live:
        return {"results": [{"topic": "live-search", "content": live, "source": "openrouter:online"}], "source": "live_search"}
    return {"results": [], "source": "none"}


@router.post("/search")
async def search(request: Request, body: QueryRequest):
    settings = Settings()
    require_marketplace_admin_secret(request, getattr(settings, "marketplace_admin_secret", ""))
    result = await search_web(body.query)
    return {"result": result}


@router.post("/council")
async def council(request: Request, body: CouncilRequest):
    settings = Settings()
    require_marketplace_admin_secret(request, getattr(settings, "marketplace_admin_secret", ""))
    from src.orchestrator import Orchestrator
    orch = Orchestrator(settings)
    await orch.initialize()
    result = await orch.execute_task({"agent_id": "council_agent", "payload": body.proposal})
    return result
