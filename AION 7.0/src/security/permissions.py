"""
JIT (Just-In-Time) Permissions + Downscoping.
Cada agente so recebe a permissao minima necessaria no momento da execucao.
"""
import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)


class JITPermissionManager:
    def __init__(self):
        self._active_tokens: dict[str, dict[str, Any]] = {}
        self._token_ttl_minutes = 5

    def request_token(
        self, agent_id: str, user_id: str, requested_scopes: list[str]
    ) -> dict[str, Any] | None:
        allowed_scopes = self._resolve_scopes(agent_id)
        granted = [s for s in requested_scopes if s in allowed_scopes]

        if not granted:
            logger.warning("JIT negado para %s: nenhum escopo valido", agent_id)
            return None

        import secrets
        token = secrets.token_hex(16)
        expires_at = datetime.utcnow() + timedelta(minutes=self._token_ttl_minutes)

        self._active_tokens[token] = {
            "agent_id": agent_id,
            "user_id": user_id,
            "scopes": granted,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at.isoformat(),
            "used": False,
        }

        logger.info(
            "JIT token emitido para %s: escopos=%s, expira=%s",
            agent_id, granted, expires_at,
        )
        return {
            "token": token,
            "scopes": granted,
            "expires_at": expires_at.isoformat(),
            "ttl_seconds": self._token_ttl_minutes * 60,
        }

    def validate_token(self, token: str, agent_id: str, required_scope: str) -> bool:
        entry = self._active_tokens.get(token)
        if not entry:
            logger.warning("JIT token invalido: %s...", token[:8])
            return False

        if entry["agent_id"] != agent_id:
            logger.warning("JIT token nao pertence a este agente")
            return False

        expires = datetime.fromisoformat(entry["expires_at"])
        if datetime.utcnow() > expires:
            logger.warning("JIT token expirado para %s", agent_id)
            del self._active_tokens[token]
            return False

        if required_scope not in entry["scopes"]:
            logger.warning("JIT escopo '%s' nao autorizado para %s", required_scope, agent_id)
            return False

        entry["used"] = True
        return True

    def revoke_token(self, token: str):
        self._active_tokens.pop(token, None)

    def revoke_all_for_agent(self, agent_id: str):
        to_revoke = [t for t, e in self._active_tokens.items() if e["agent_id"] == agent_id]
        for t in to_revoke:
            del self._active_tokens[t]
        logger.info("JIT tokens revogados para %s: %d", agent_id, len(to_revoke))

    def _resolve_scopes(self, agent_id: str) -> list[str]:
        scopes = {
            "spec_analyst": ["documentos:ler", "analises:criar"],
            "procurement": ["compras:criar", "fornecedores:consultar"],
            "inventory": ["estoque:ler", "estoque:atualizar"],
            "logistics": ["envios:rastrear", "notas:gerar"],
            "field_execution": ["instrucoes:criar", "campo:ler"],
            "bim_coordinator": ["bim:criar", "bim:validar"],
            "requirements_analyst": ["requisitos:analisar"],
            "engineering_assistant": ["perguntas:responder"],
            "work_synopsis": ["resumos:criar"],
            "photo_intelligence": ["fotos:analisar"],
            "rfi_creation": ["rfis:criar"],
            "compliance": ["conformidade:analisar"],
            "diagnostic": ["residuos:classificar"],
            "monitoring": ["prazos:monitorar", "alertas:gerar"],
        }
        return scopes.get(agent_id, [])

    def cleanup_expired(self):
        now = datetime.utcnow()
        expired = [t for t, e in self._active_tokens.items()
                   if datetime.fromisoformat(e["expires_at"]) <= now]
        for t in expired:
            del self._active_tokens[t]
        if expired:
            logger.info("JIT cleanup: %d tokens expirados removidos", len(expired))
