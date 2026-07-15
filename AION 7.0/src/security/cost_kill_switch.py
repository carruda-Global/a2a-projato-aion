"""
Cost Kill-Switch: Limite de custo por execucao de agente (US$ 1/exec).
Evita surpresas na fatura da API.

DeepSeek-V4-Flash custa ~US$ 0.15/1M tokens input, ~US$ 0.60/1M tokens output.
Com 16K tokens por execucao, cada chamada custa ~US$ 0.004-0.01.
Limite de US$ 1/exec permite ~100-250 chamadas antes do alerta.
"""
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

COST_PER_TOKEN_INPUT_USD = 0.00000015
COST_PER_TOKEN_OUTPUT_USD = 0.00000060
MAX_COST_PER_EXECUTION_USD = 1.0
MAX_TOKENS_PER_EXECUTION = 16000
WARN_COST_USD = 0.50


class CostKillSwitch:
    def __init__(self):
        self._usage: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._daily_budget: dict[str, float] = defaultdict(float)
        self._global_daily_budget = 50.0  # US$ 50/dia global

    def check(self, agent_id: str, estimated_tokens: int = MAX_TOKENS_PER_EXECUTION) -> tuple[bool, str]:
        estimated_cost = self._estimate_cost(agent_id, estimated_tokens)

        if estimated_cost > MAX_COST_PER_EXECUTION_USD:
            logger.warning(
                "KILL-SWITCH: %s excederia US$ %.2f (custo estimado: US$ %.4f)",
                agent_id, MAX_COST_PER_EXECUTION_USD, estimated_cost,
            )
            return False, f"Custo estimado US$ {estimated_cost:.4f} excede limite de US$ {MAX_COST_PER_EXECUTION_USD}"

        today = datetime.utcnow().date().isoformat()
        if self._daily_budget[today] + estimated_cost > self._global_daily_budget:
            logger.warning(
                "KILL-SWITCH: orcamento diario global excedido (US$ %.2f / US$ %.2f)",
                self._daily_budget[today], self._global_daily_budget,
            )
            return False, f"Orcamento diario de US$ {self._global_daily_budget:.2f} excedido"

        if estimated_cost >= WARN_COST_USD:
            logger.info(
                "ALERTA CUSTO: %s estimado em US$ %.4f (> US$ %.2f)",
                agent_id, estimated_cost, WARN_COST_USD,
            )

        return True, "ok"

    def record_execution(self, agent_id: str, tokens_input: int, tokens_output: int):
        cost = (tokens_input * COST_PER_TOKEN_INPUT_USD +
                tokens_output * COST_PER_TOKEN_OUTPUT_USD)
        today = datetime.utcnow().date().isoformat()

        entry = {
            "agent_id": agent_id,
            "tokens_input": tokens_input,
            "tokens_output": tokens_output,
            "cost_usd": round(cost, 6),
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._usage[agent_id].append(entry)
        self._daily_budget[today] += cost

        logger.info(
            "CUSTO %s: input=%d output=%d custo=US$ %.6f (diario=US$ %.4f)",
            agent_id, tokens_input, tokens_output, cost, self._daily_budget[today],
        )

    def get_usage(self, agent_id: str | None = None, days: int = 7) -> dict[str, Any]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        total_cost = 0.0
        total_tokens = 0
        call_count = 0

        agents_to_check = [agent_id] if agent_id else list(self._usage.keys())
        result: dict[str, Any] = {"total_cost_usd": 0, "total_calls": 0, "agents": {}}

        for aid in agents_to_check:
            agent_calls = [e for e in self._usage.get(aid, [])
                           if datetime.fromisoformat(e["timestamp"]) > cutoff]
            agent_cost = sum(e["cost_usd"] for e in agent_calls)
            result["agents"][aid] = {
                "calls": len(agent_calls),
                "cost_usd": round(agent_cost, 4),
                "tokens": sum(e["tokens_input"] + e["tokens_output"] for e in agent_calls),
            }
            total_cost += agent_cost
            total_tokens += sum(e["tokens_input"] + e["tokens_output"] for e in agent_calls)
            call_count += len(agent_calls)

        result["total_cost_usd"] = round(total_cost, 4)
        result["total_calls"] = call_count
        result["period_days"] = days
        return result

    def _estimate_cost(self, agent_id: str, tokens: int) -> float:
        avg_input_ratio = 0.7
        input_tokens = int(tokens * avg_input_ratio)
        output_tokens = tokens - input_tokens
        return (input_tokens * COST_PER_TOKEN_INPUT_USD +
                output_tokens * COST_PER_TOKEN_OUTPUT_USD)
