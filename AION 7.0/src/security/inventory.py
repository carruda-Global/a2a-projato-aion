"""
Inventario de agentes, dados acessados e superficie de ataque.
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentAccess:
    agent_id: str
    name: str
    data_categories: list[str]
    input_type: str
    output_type: str
    external_calls: list[str]
    risk_level: str  # baixo | medio | alto | critico
    requires_human_review: bool = False
    max_tokens_per_call: int = 16384
    monthly_limit: int = 1000


AGENT_INVENTORY: list[AgentAccess] = [
    AgentAccess(
        agent_id="spec_analyst", name="Spec Analyst",
        data_categories=["documentos_engenharia", "normas_tecnicas", "memoriais_descritivos"],
        input_type="texto", output_type="analise_texto",
        external_calls=["DeepSeek API"], risk_level="medio",
    ),
    AgentAccess(
        agent_id="procurement", name="Procurement",
        data_categories=["pedidos_compra", "cotacoes", "fornecedores"],
        input_type="json_estruturado", output_type="plano_compra",
        external_calls=["DeepSeek API"], risk_level="medio",
    ),
    AgentAccess(
        agent_id="inventory", name="Inventory",
        data_categories=["estoque_obra", "materiais", "niveis_reposicao"],
        input_type="json_estruturado", output_type="analise_estoque",
        external_calls=["DeepSeek API"], risk_level="baixo",
    ),
    AgentAccess(
        agent_id="logistics", name="Logistics",
        data_categories=["envios", "transportadoras", "notas_fiscais"],
        input_type="json", output_type="analise_logistica",
        external_calls=["DeepSeek API"], risk_level="medio",
    ),
    AgentAccess(
        agent_id="field_execution", name="Field Execution",
        data_categories=["instrucoes_obra", "projetos_bim", "especificacoes"],
        input_type="texto", output_type="instrucoes_campo",
        external_calls=["DeepSeek API"], risk_level="alto",
        requires_human_review=True,
    ),
    AgentAccess(
        agent_id="bim_coordinator", name="BIM Coordinator",
        data_categories=["modelos_bim", "elementos_3d", "conflitos"],
        input_type="texto", output_type="especificacoes_bim",
        external_calls=["DeepSeek API"], risk_level="medio",
    ),
    AgentAccess(
        agent_id="requirements_analyst", name="Requirements Analyst",
        data_categories=["requisitos_engenharia", "padroes_qualidade"],
        input_type="texto", output_type="analise_qualidade",
        external_calls=["DeepSeek API"], risk_level="baixo",
    ),
    AgentAccess(
        agent_id="engineering_assistant", name="Engineering Assistant",
        data_categories=["perguntas_tecnicas", "documentos", "normas"],
        input_type="texto", output_type="respostas",
        external_calls=["DeepSeek API"], risk_level="baixo",
    ),
    AgentAccess(
        agent_id="work_synopsis", name="Work Synopsis",
        data_categories=["tarefas_obra", "defeitos", "cronograma"],
        input_type="texto", output_type="resumo",
        external_calls=["DeepSeek API"], risk_level="baixo",
    ),
    AgentAccess(
        agent_id="photo_intelligence", name="Photo Intelligence",
        data_categories=["fotos_obra", "descricoes_visuais", "epi"],
        input_type="texto", output_type="analise_visual",
        external_calls=["DeepSeek API"], risk_level="medio",
    ),
    AgentAccess(
        agent_id="rfi_creation", name="RFI Creation",
        data_categories=["duvidas_campo", "especificacoes", "documentacao"],
        input_type="texto", output_type="rfi",
        external_calls=["DeepSeek API"], risk_level="medio",
    ),
    AgentAccess(
        agent_id="compliance", name="Compliance",
        data_categories=["dados_empresa", "normas_ambientais", "legislacao"],
        input_type="texto", output_type="relatorio_conformidade",
        external_calls=["DeepSeek API"], risk_level="critico",
        requires_human_review=True,
    ),
    AgentAccess(
        agent_id="diagnostic", name="Diagnostic",
        data_categories=["classificacao_residuos", "nbr_10004", "processos_empresa"],
        input_type="texto", output_type="classificacao",
        external_calls=["DeepSeek API"], risk_level="alto",
    ),
    AgentAccess(
        agent_id="monitoring", name="Monitoring",
        data_categories=["prazos_renovacao", "alertas", "historico_conformidade"],
        input_type="texto", output_type="plano_monitoramento",
        external_calls=["DeepSeek API"], risk_level="baixo",
    ),
]


class AgentInventory:
    def get_all(self) -> list[AgentAccess]:
        return AGENT_INVENTORY

    def get_by_id(self, agent_id: str) -> AgentAccess | None:
        for a in AGENT_INVENTORY:
            if a.agent_id == agent_id:
                return a
        return None

    def get_risk_summary(self) -> dict[str, list[str]]:
        summary: dict[str, list[str]] = {"critico": [], "alto": [], "medio": [], "baixo": []}
        for a in AGENT_INVENTORY:
            summary[a.risk_level].append(a.agent_id)
        return summary

    def get_attack_surface(self) -> list[dict[str, Any]]:
        return [
            {
                "agent_id": a.agent_id,
                "risk": a.risk_level,
                "data": a.data_categories,
                "external_calls": a.external_calls,
                "needs_review": a.requires_human_review,
            }
            for a in AGENT_INVENTORY
        ]
