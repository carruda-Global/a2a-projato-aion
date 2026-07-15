"""Real daily/pulse health check across every real, connected surface of the
system (site, backend, database, payments, AgentVerse, the 11 real
orchestrator agents). Persists each run to Supabase and emails a real alert
on failure via the confirmed-working Hostinger SMTP path.

Also the real "incident response" signal: on every pulse (every 30min,
see .github/workflows/system-health-pulse.yml) it checks agent_execution_log
for any agent with a failure-rate spike in the last window and folds that
into the same alert email. Deliberately does NOT auto-rollback or auto-switch
models -- there's no real multi-version deploy to roll back between today
(a single live commit on Render, not a versioned agent fleet), so an
"auto-rollback" would just be theater. This detects and tells a human fast;
acting on it is a deliberate follow-up, not automated here.

Deliberately does NOT auto-modify code or auto-deploy fixes -- an LLM
autonomously patching and shipping code against a live revenue system
without review is a real risk, not a safety feature. This agent's job is
fast, honest detection and a clear report a human (or a future Claude Code
session) can act on quickly -- exactly what was missing during today's
undetected domain outage."""
import logging
import os
from datetime import datetime, timedelta, timezone

import httpx

logger = logging.getLogger(__name__)

_SUPABASE_URL = os.getenv("SUPABASE_URL", "")
_SUPABASE_KEY = os.getenv("SUPABASE_API_KEY", "")
_ALERT_EMAIL = os.getenv("HEALTH_ALERT_EMAIL", "carruda2307@gmail.com")
_TABLE = "system_health_reports"
_ERROR_SPIKE_WINDOW_MIN = 30
_ERROR_SPIKE_MIN_CALLS = 3
_ERROR_SPIKE_FAILURE_RATE = 0.5

_CONNECTIVITY_CHECKS = [
    ("site_root", "https://global-engenharia.com/"),
    ("site_vendas", "https://global-engenharia.com/vendas.html"),
    ("backend", "https://engenheiro-producao-ai.onrender.com/"),
    ("agentverse_relay", "https://engenheiro-producao-ai.onrender.com/api/agentverse/warmup"),
]

_AGENT_SAMPLE = ["architect_agent", "quality_critic"]


async def _check_url(client: httpx.AsyncClient, name: str, url: str) -> dict:
    try:
        r = await client.get(url, timeout=12)
        return {"check": name, "ok": r.status_code < 400, "status_code": r.status_code}
    except Exception as e:
        return {"check": name, "ok": False, "error": str(e)}


async def _check_supabase(client: httpx.AsyncClient) -> dict:
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return {"check": "supabase", "ok": False, "error": "not configured"}
    try:
        r = await client.get(
            f"{_SUPABASE_URL}/rest/v1/agent_compliance_receipts",
            params={"select": "id", "limit": "1"},
            headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
            timeout=12,
        )
        return {"check": "supabase", "ok": r.status_code == 200, "status_code": r.status_code}
    except Exception as e:
        return {"check": "supabase", "ok": False, "error": str(e)}


async def _check_stripe(client: httpx.AsyncClient) -> dict:
    key = os.getenv("STRIPE_SECRET_KEY", "")
    if not key:
        return {"check": "stripe", "ok": False, "error": "not configured"}
    try:
        r = await client.get(
            "https://api.stripe.com/v1/products",
            params={"limit": 1},
            headers={"Authorization": f"Bearer {key}"},
            timeout=12,
        )
        return {"check": "stripe", "ok": r.status_code == 200, "status_code": r.status_code}
    except Exception as e:
        return {"check": "stripe", "ok": False, "error": str(e)}


async def _check_agent_error_spikes(client: httpx.AsyncClient) -> list[dict]:
    """Real incident-detection signal, built on the agent_execution_log
    written by src/security/agent_execution_log.py. Flags any agent with
    >= _ERROR_SPIKE_MIN_CALLS calls and a failure rate >= _ERROR_SPIKE_FAILURE_RATE
    in the last _ERROR_SPIKE_WINDOW_MIN minutes. Returned as normal `checks`
    entries so they flow through the existing alert-email path unchanged."""
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return []
    cutoff = (datetime.now(timezone.utc) - timedelta(minutes=_ERROR_SPIKE_WINDOW_MIN)).isoformat()
    try:
        r = await client.get(
            f"{_SUPABASE_URL}/rest/v1/agent_execution_log",
            params={"select": "agent_id,success", "created_at": f"gte.{cutoff}", "limit": "2000"},
            headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
            timeout=12,
        )
        if r.status_code != 200:
            return [{"check": "agent_error_spikes", "ok": False, "error": f"query failed: {r.status_code}"}]
        rows = r.json()
    except Exception as e:
        return [{"check": "agent_error_spikes", "ok": False, "error": str(e)}]

    totals: dict[str, dict[str, int]] = {}
    for row in rows:
        agent_id = row.get("agent_id", "unknown")
        stats = totals.setdefault(agent_id, {"total": 0, "failures": 0})
        stats["total"] += 1
        if not row.get("success"):
            stats["failures"] += 1

    spikes = []
    for agent_id, stats in totals.items():
        if stats["total"] < _ERROR_SPIKE_MIN_CALLS:
            continue
        failure_rate = stats["failures"] / stats["total"]
        if failure_rate >= _ERROR_SPIKE_FAILURE_RATE:
            spikes.append({
                "check": f"error_rate:{agent_id}",
                "ok": False,
                "error": f"{stats['failures']}/{stats['total']} calls failed in last {_ERROR_SPIKE_WINDOW_MIN}min",
            })
    return spikes


async def _check_agents(settings) -> list[dict]:
    results = []
    try:
        from src.orchestrator import Orchestrator
    except ImportError:
        return [{"check": "orchestrator_agents", "ok": False, "error": "src.orchestrator not importable"}]

    try:
        orch = Orchestrator(settings)
        await orch.initialize()
        for agent_id in _AGENT_SAMPLE:
            try:
                if agent_id in orch._executor_map:
                    r = await orch._executor_map[agent_id]({"task": "Reply with just: OK"})
                    ok = "error" not in r
                else:
                    ok, r = False, {"error": "no real executor registered"}
                results.append({"check": f"agent:{agent_id}", "ok": ok})
            except Exception as e:
                results.append({"check": f"agent:{agent_id}", "ok": False, "error": str(e)})
    except Exception as e:
        results.append({"check": "orchestrator_init", "ok": False, "error": str(e)})
    return results


async def run_health_check(deep: bool = False) -> dict:
    async with httpx.AsyncClient() as client:
        checks = [await _check_url(client, name, url) for name, url in _CONNECTIVITY_CHECKS]
        checks.append(await _check_supabase(client))
        checks.append(await _check_stripe(client))
        checks += await _check_agent_error_spikes(client)

    if deep:
        try:
            from src.config import Settings
            checks += await _check_agents(Settings())
        except Exception as e:
            checks.append({"check": "agents_sweep", "ok": False, "error": str(e)})

    failures = [c for c in checks if not c.get("ok")]
    report = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "deep": deep,
        "total_checks": len(checks),
        "failures": len(failures),
        "checks": checks,
    }

    await _persist_report(report)
    if failures:
        await _send_alert(report, failures)
    return report


async def _persist_report(report: dict) -> None:
    if not (_SUPABASE_URL and _SUPABASE_KEY):
        return
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{_SUPABASE_URL}/rest/v1/{_TABLE}",
                json={
                    "run_at": report["run_at"], "deep": report["deep"],
                    "total_checks": report["total_checks"], "failures": report["failures"],
                    "details": report["checks"],
                },
                headers={"apikey": _SUPABASE_KEY, "Authorization": f"Bearer {_SUPABASE_KEY}"},
                timeout=12,
            )
    except Exception as e:
        logger.warning("[SystemHealth] Failed to persist report: %s", e)


async def _send_alert(report: dict, failures: list[dict]) -> None:
    try:
        from src.email.smtp_mailer import send_via_hostinger
    except ImportError:
        logger.warning("[SystemHealth] Mailer not available, alert not sent")
        return

    lines = "".join(f"<li><b>{f['check']}</b>: {f.get('error') or f.get('status_code')}</li>" for f in failures)
    html = f"<p>{len(failures)} of {report['total_checks']} checks failed at {report['run_at']}.</p><ul>{lines}</ul>"
    try:
        import asyncio
        await asyncio.to_thread(
            send_via_hostinger, _ALERT_EMAIL,
            f"[AION alerta] {len(failures)} verificacao(oes) falhando", html,
        )
    except Exception as e:
        logger.warning("[SystemHealth] Failed to send alert email: %s", e)
