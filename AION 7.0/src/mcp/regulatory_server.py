from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.mcp.base_server import MCPServer, MCPTool

regulatory_app = FastAPI(title="Ecosystem Regulatory MCP Server", version="3.0.0")

mcp = MCPServer(
    server_id="ecosystem-regulatory",
    name="Ecosystem Regulatory MCP",
    description="Agentes regulatórios brasileiros — NR-1, LGPD, CBS/IBS, Denúncias, Igualdade Salarial, Anticorrupção, Onboarding, Conciliação"
)

def _nr1_psicossocial(dados_empresa: str = "") -> dict:
    return {
        "tool": "nr1_psicossocial",
        "status": "simulated",
        "message": "Inventário de Riscos Psicossociais gerado conforme Portaria MTE 1.419/2024",
        "riscos_identificados": 5,
        "plano_acao": "Plano de ação com 3 medidas prioritárias",
    }

def _lgpd_operacional(dados_empresa: str = "") -> dict:
    return {
        "tool": "lgpd_operacional",
        "status": "simulated",
        "message": "RoPA gerado conforme Lei 13.709/2018",
        "fluxos_mapeados": 8,
        "lacunas_identificadas": 2,
    }

def _tributario_cbs_ibs(descricao: str = "") -> dict:
    return {
        "tool": "tributario_cbs_ibs",
        "status": "simulated",
        "message": "Classificação CBS/IBS conforme LC 214/2025",
        "ncm_classificado": "8471.30.00",
        "aliquota_cbs": 8.5,
        "aliquota_ibs": 7.0,
    }

def _canal_denuncias(denuncia: str = "") -> dict:
    return {
        "tool": "canal_denuncias",
        "status": "simulated",
        "message": "Denúncia classificada conforme Lei 14.457/2022",
        "categoria": "assedio_moral",
        "gravidade": "media",
        "encaminhamento": "Investigação interna em até 48h",
    }

def _igualdade_salarial(dados_folha: str = "") -> dict:
    return {
        "tool": "igualdade_salarial",
        "status": "simulated",
        "message": "Relatório de equidade salarial gerado conforme Lei 14.611/2023",
        "gap_medio": 12.5,
        "recomendacoes": 3,
    }

def _compliance_anticorrupcao(dados_empresa: str = "") -> dict:
    return {
        "tool": "compliance_anticorrupcao",
        "status": "simulated",
        "message": "Diagnóstico de maturidade conforme Lei 12.846/2013",
        "maturidade": "media",
        "recomendacoes": ["Código de Ética", "Canal de Denúncias", "Treinamento"],
    }

def _onboarding_funcionarios(dados_funcionario: str = "") -> dict:
    return {
        "tool": "onboarding_funcionarios",
        "status": "simulated",
        "message": "Checklist de admissão gerado",
        "etapas": ["Documentos", "Contrato", "eSocial", "Acessos M365"],
        "status_geral": "pendente_aprovacao",
    }

def _conciliacao_financeira(extrato: str = "", notas_fiscais: str = "") -> dict:
    return {
        "tool": "conciliacao_financeira",
        "status": "simulated",
        "message": "Conciliação realizada",
        "nfs_conciliadas": 45,
        "divergencias": 3,
        "valor_total_conciliado": 125000.00,
    }

mcp.register_tool(MCPTool(
    name="nr1_psicossocial", description="Inventário de riscos psicossociais NR-1 (Portaria MTE 1.419/2024)",
    handler=_nr1_psicossocial, sensitive=True,
    parameters={"dados_empresa": {"type": "string", "description": "Dados da empresa para análise"}}
))
mcp.register_tool(MCPTool(
    name="lgpd_operacional", description="Mapeamento LGPD e RoPA (Lei 13.709/2018)",
    handler=_lgpd_operacional, sensitive=True,
    parameters={"dados_empresa": {"type": "string"}}
))
mcp.register_tool(MCPTool(
    name="tributario_cbs_ibs", description="Classificação CBS/IBS (LC 214/2025)",
    handler=_tributario_cbs_ibs,
    parameters={"descricao": {"type": "string", "description": "Descrição do produto/serviço"}}
))
mcp.register_tool(MCPTool(
    name="canal_denuncias", description="Classificação e triagem de denúncias (Lei 14.457/2022)",
    handler=_canal_denuncias, sensitive=True,
    parameters={"denuncia": {"type": "string", "description": "Relato da denúncia"}}
))
mcp.register_tool(MCPTool(
    name="igualdade_salarial", description="Relatório de equidade salarial (Lei 14.611/2023)",
    handler=_igualdade_salarial, sensitive=True,
    parameters={"dados_folha": {"type": "string"}}
))
mcp.register_tool(MCPTool(
    name="compliance_anticorrupcao", description="Programa de integridade (Lei 12.846/2013)",
    handler=_compliance_anticorrupcao, sensitive=True,
    parameters={"dados_empresa": {"type": "string"}}
))
mcp.register_tool(MCPTool(
    name="onboarding_funcionarios", description="Checklist automatizado de admissão",
    handler=_onboarding_funcionarios, sensitive=True,
    parameters={"dados_funcionario": {"type": "string"}}
))
mcp.register_tool(MCPTool(
    name="conciliacao_financeira", description="Conciliação de NFs com extratos bancários",
    handler=_conciliacao_financeira,
    parameters={"extrato": {"type": "string"}, "notas_fiscais": {"type": "string"}}
))


class ToolCallRequest(BaseModel):
    tool: str
    params: dict = {}
    tenant_id: str = "default"


@regulatory_app.get("/health")
async def health():
    return {"status": "healthy", "server": mcp.server_id}


@regulatory_app.get("/mcp/manifest")
async def manifest():
    return mcp.manifest()


@regulatory_app.get("/mcp/tools")
async def list_tools():
    return {"tools": mcp.get_tools_list()}


@regulatory_app.post("/mcp/call")
async def call_tool(req: ToolCallRequest):
    result = await mcp.call_tool(req.tool, req.params, req.tenant_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
