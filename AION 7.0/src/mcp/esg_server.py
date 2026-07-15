from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.mcp.base_server import MCPServer, MCPTool

esg_app = FastAPI(title="Ecosystem ESG MCP Server", version="3.0.0")

mcp = MCPServer(
    server_id="ecosystem-esg",
    name="Ecosystem ESG MCP",
    description="Agentes ESG — IFRS S1/S2, Inventário Carbono, Escopo 3, CBAM"
)

def _esg_ifrs_diagnostico(dados_empresa: str = "") -> dict:
    return {
        "tool": "esg_ifrs_diagnostico",
        "status": "simulated",
        "message": "Diagnóstico ESG concluído conforme IFRS S1/S2 (Res. CVM 193/2023)",
        "maturidade": "inicial",
        "indicadores_materiais": ["GEE", "Diversidade", "Segurança"],
        "score": 35,
    }

def _inventario_carbono(dados_consumo: str = "") -> dict:
    return {
        "tool": "inventario_carbono",
        "status": "simulated",
        "message": "Inventário GHG Protocol Escopo 1 e 2 calculado",
        "escopo_1_tco2e": 450.0,
        "escopo_2_tco2e": 280.0,
        "total_tco2e": 730.0,
        "metodologia": "GHG Protocol + MCTI",
    }

def _escopo3_fornecedores(dados_cadeia: str = "") -> dict:
    return {
        "tool": "escopo3_fornecedores",
        "status": "simulated",
        "message": "Avaliação Escopo 3 realizada — 15 categorias GHG",
        "fornecedores_mapeados": 25,
        "emissoes_estimadas_tco2e": 3200.0,
        "categorias_prioritarias": ["Bens adquiridos", "Transporte upstream"],
    }

def _cbam_certificate(dados_exportacao: str = "") -> dict:
    return {
        "tool": "cbam_certificate",
        "status": "simulated",
        "message": "Certificado CBAM gerado conforme Reg. UE 2023/956",
        "produto": "Cimento Portland",
        "ncm": "2523.10.00",
        "emissoes_incorporadas_tco2e": 180.0,
        "preco_cbam_estimado_eur": 4500.0,
    }

mcp.register_tool(MCPTool(
    name="esg_ifrs_diagnostico", description="Diagnóstico ESG IFRS S1/S2",
    handler=_esg_ifrs_diagnostico,
    parameters={"dados_empresa": {"type": "string"}}
))
mcp.register_tool(MCPTool(
    name="inventario_carbono", description="Inventário GHG Protocol Escopo 1/2",
    handler=_inventario_carbono,
    parameters={"dados_consumo": {"type": "string"}}
))
mcp.register_tool(MCPTool(
    name="escopo3_fornecedores", description="Rastreabilidade Escopo 3",
    handler=_escopo3_fornecedores,
    parameters={"dados_cadeia": {"type": "string"}}
))
mcp.register_tool(MCPTool(
    name="cbam_certificate", description="Certificado CBAM (Reg. UE 2023/956)",
    handler=_cbam_certificate,
    parameters={"dados_exportacao": {"type": "string"}}
))


class ToolCallRequest(BaseModel):
    tool: str
    params: dict = {}
    tenant_id: str = "default"


@esg_app.get("/health")
async def health():
    return {"status": "healthy", "server": mcp.server_id}


@esg_app.get("/mcp/manifest")
async def manifest():
    return mcp.manifest()


@esg_app.get("/mcp/tools")
async def list_tools():
    return {"tools": mcp.get_tools_list()}


@esg_app.post("/mcp/call")
async def call_tool(req: ToolCallRequest):
    result = await mcp.call_tool(req.tool, req.params, req.tenant_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
