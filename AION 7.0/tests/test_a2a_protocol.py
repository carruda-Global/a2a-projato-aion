import pytest
from unittest.mock import patch, MagicMock
from httpx import ASGITransport, AsyncClient

from app.main import app

import_mark = pytest.mark.asyncio

skip_integration = pytest.mark.skipif(
    True,
    reason="Integration tests require running API",
)


@pytest.mark.integration
@skip_integration
class TestA2AProtocol:
    @pytest.fixture
    def client(self):
        return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    async def test_agent_card_endpoint(self, client):
        response = await client.get("/.well-known/agent-card.json")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Engenheiro de Produção AI"
        assert "skills" in data
        assert len(data["skills"]) == 27

    async def test_agent_card_has_all_skills(self, client):
        response = await client.get("/.well-known/agent-card.json")
        data = response.json()
        skill_ids = {s["id"] for s in data["skills"]}
        expected = {
            "spec_analysis", "procurement", "inventory", "logistics",
            "field_execution", "bim_coordination", "requirements_analysis",
            "engineering_assistant", "work_synopsis", "photo_intelligence",
            "rfi_creation", "compliance",
            "nr1_psicossocial", "tributario_cbs_ibs", "lgpd_operacional",
            "esg_ifrs", "inventario_carbono", "escopo3_fornecedores",
            "canal_denuncias", "igualdade_salarial", "compliance_anticorrupcao",
            "regulatory_analyst", "compliance_pm", "channel_agent",
            "knowledge_agent", "facilitator_agent", "dev_experience",
        }
        assert skill_ids == expected

    async def test_agent_card_has_security_schemes(self, client):
        response = await client.get("/.well-known/agent-card.json")
        data = response.json()
        assert "securitySchemes" in data
        assert "api_key" in data["securitySchemes"]

    async def test_agent_card_has_interfaces(self, client):
        response = await client.get("/.well-known/agent-card.json")
        data = response.json()
        assert "supportedInterfaces" in data
        bindings = {i["protocolBinding"] for i in data["supportedInterfaces"]}
        assert "JSONRPC" in bindings
        assert "HTTP+JSON" in bindings

    async def test_agent_card_capabilities(self, client):
        response = await client.get("/.well-known/agent-card.json")
        data = response.json()
        assert data["capabilities"]["streaming"] is True

    async def test_jsonrpc_method_not_found(self, client):
        payload = {
            "jsonrpc": "2.0",
            "method": "UnknownMethod",
            "id": 1,
        }
        response = await client.post("/a2a/jsonrpc", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["error"]["code"] == -32601

    async def test_jsonrpc_send_message_missing_params(self, client):
        payload = {
            "jsonrpc": "2.0",
            "method": "SendMessage",
            "id": 1,
        }
        response = await client.post("/a2a/jsonrpc", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "error" in data

    async def test_rest_send_message_no_auth(self, client):
        response = await client.post(
            "/a2a/rest/message:send",
            json={"message": {"role": "user", "parts": [{"text": "test"}]}},
        )
        assert response.status_code == 200
        data = response.json()
        assert "result" in data or "error" in data

    async def test_a2a_routes_listed_in_openapi(self, client):
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        paths = response.json().get("paths", {})
        a2a_paths = [p for p in paths if "a2a" in p]
        assert len(a2a_paths) > 0


@pytest.mark.unit
class TestAgentCardBuilder:
    def test_build_card_default_url(self):
        from src.a2a_bridge.agent_cards import build_agent_card

        card = build_agent_card()
        assert "Engenheiro" in card.name
        assert len(card.skills) == 27
        assert card.capabilities.streaming

    def test_build_card_custom_url(self):
        from src.a2a_bridge.agent_cards import build_agent_card

        card = build_agent_card(base_url="https://custom.example.com")
        for iface in card.supported_interfaces:
            assert "custom.example.com" in iface.url

    def test_skills_have_required_fields(self):
        from src.a2a_bridge.agent_cards import build_agent_card

        card = build_agent_card()
        assert len(card.skills) == 27
        for skill in card.skills:
            assert skill.id
            assert skill.name
            assert skill.description
            assert len(skill.tags) > 0
            assert len(skill.examples) > 0
            assert "text" in list(skill.input_modes)
            assert "text" in list(skill.output_modes)


@pytest.mark.unit
class TestSkillMap:
    def test_all_agents_mapped(self):
        from src.a2a_bridge.executors import SKILL_MAP

        assert SKILL_MAP["spec_analysis"] == "spec_analyst"
        assert SKILL_MAP["procurement"] == "procurement"
        assert SKILL_MAP["inventory"] == "inventory"
        assert SKILL_MAP["logistics"] == "logistics"
        assert SKILL_MAP["field_execution"] == "field_execution"

    def test_all_internal_agents_covered(self):
        from src.a2a_bridge.executors import SKILL_MAP

        internal_ids = set(SKILL_MAP.values())
        expected = {
            "spec_analyst", "procurement", "inventory", "logistics",
            "field_execution", "bim_coordinator", "requirements_analyst",
            "engineering_assistant", "work_synopsis", "photo_intelligence",
            "rfi_creation", "compliance",
            "nr1_psicossocial", "tributario_cbs_ibs", "lgpd_operacional",
            "esg_ifrs", "inventario_carbono", "escopo3_fornecedores",
            "canal_denuncias", "igualdade_salarial", "compliance_anticorrupcao",
            "regulatory_analyst", "compliance_pm", "channel_agent",
            "knowledge_agent", "facilitator_agent", "dev_experience",
        }
        assert internal_ids == expected
