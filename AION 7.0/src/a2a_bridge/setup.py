import logging

from fastapi import FastAPI

from a2a.server.tasks import InMemoryTaskStore
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import (
    add_a2a_routes_to_fastapi,
    create_agent_card_routes,
    create_jsonrpc_routes,
    create_rest_routes,
)
from src.config import Settings
from .agent_cards import build_agent_card
from .executors import AECAgentExecutor

logger = logging.getLogger(__name__)


def _patch_a2a_sdk_field_schema_bug() -> None:
    """a2a-sdk 1.1.0's _proto_schema.field_schema() calls field.is_repeated,
    which doesn't exist on the standard protobuf FieldDescriptor API (confirmed
    against both the C++/upb and pure-Python backends) -- crashes JSON-RPC
    route setup on every startup with AttributeError. Real upstream bug, not
    fixable in our own code short of this monkey-patch; the correct
    equivalent is field.label == FieldDescriptor.LABEL_REPEATED. Safe/narrow:
    only replaces this one function, leaves everything else untouched, and is
    a no-op if a future a2a-sdk release fixes it upstream (this just
    overwrites the (already working) function again)."""
    from google.protobuf.descriptor import FieldDescriptor
    from a2a.server.routes import _proto_schema

    original_message_schema = _proto_schema.message_schema

    def _patched_field_schema(field, components):
        if field.type == FieldDescriptor.TYPE_MESSAGE:
            item = original_message_schema(field.message_type, components)
        elif field.type == FieldDescriptor.TYPE_ENUM:
            item = {"type": "string", "enum": [v.name for v in field.enum_type.values]}
        else:
            item = dict(_proto_schema._PROTO_SCALAR_SCHEMAS.get(field.type, {"type": "string"}))

        if field.label == FieldDescriptor.LABEL_REPEATED:
            return {"type": "array", "items": item}
        return item

    _proto_schema.field_schema = _patched_field_schema
    logger.info("[A2A] Patched a2a-sdk field_schema() is_repeated bug")


def setup_a2a_routes(
    app: FastAPI,
    settings: Settings,
    base_url: str | None = None,
    enable_v0_3_compat: bool = False,
):
    _patch_a2a_sdk_field_schema_bug()

    agent_card = build_agent_card(base_url=base_url)
    agent_executor = AECAgentExecutor(settings)
    task_store = InMemoryTaskStore()

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=task_store,
        agent_card=agent_card,
    )

    agent_card_routes = create_agent_card_routes(agent_card)
    jsonrpc_routes = create_jsonrpc_routes(
        request_handler=request_handler,
        rpc_url="/a2a/jsonrpc",
        enable_v0_3_compat=enable_v0_3_compat,
    )
    rest_routes = create_rest_routes(
        request_handler=request_handler,
        path_prefix="/a2a/rest",
        enable_v0_3_compat=enable_v0_3_compat,
    )

    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=agent_card_routes,
        jsonrpc_routes=jsonrpc_routes,
        rest_routes=rest_routes,
    )

    logger.info(
        "A2A Protocol routes mounted: "
        "AgentCard=/.well-known/agent-card.json, "
        "JSONRPC=/a2a/jsonrpc, "
        "REST=/a2a/rest"
    )
