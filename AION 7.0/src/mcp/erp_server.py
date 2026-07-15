from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.mcp.base_server import MCPServer, MCPTool

erp_app = FastAPI(title="Ecosystem ERP MCP Server", version="3.0.0")

mcp = MCPServer(
    server_id="ecosystem-erp",
    name="Ecosystem ERP MCP",
    description="Agentes ERP — Dynamics 365"
)

def _dynamics_sales(pipeline_data: str = "") -> dict:
    return {"tool": "dynamics_sales", "status": "simulated", "message": "Pipeline D365 analisado", "deals_at_risk": 3, "forecast_brl": 850000.0}

def _dynamics_finance(period: str = "current_month") -> dict:
    return {"tool": "dynamics_finance", "status": "simulated", "message": "Fluxo de caixa D365 analisado", "receivables_brl": 320000.0, "payables_brl": 280000.0}

def _dynamics_hr(payroll_data: str = "") -> dict:
    return {"tool": "dynamics_hr", "status": "simulated", "message": "Folha D365 analisada conforme Lei 14.611/2023", "equity_gap_pct": 12.3}

def _powerbi_compliance(tenant_data: str = "") -> dict:
    return {"tool": "powerbi_compliance", "status": "simulated", "message": "Dashboard Power BI gerado", "overall_score_pct": 62.0, "urgent_items": ["Completar mapeamento LGPD"]}

mcp.register_tool(MCPTool(name="dynamics_sales", description="Analisa pipeline Dynamics 365 Sales", handler=_dynamics_sales, parameters={"pipeline_data": {"type": "string"}}))
mcp.register_tool(MCPTool(name="dynamics_finance", description="Analisa fluxo de caixa Dynamics 365 Finance", handler=_dynamics_finance, parameters={"period": {"type": "string"}}))
mcp.register_tool(MCPTool(name="dynamics_hr", description="Analisa equidade salarial Dynamics 365 HR", handler=_dynamics_hr, parameters={"payroll_data": {"type": "string"}}, sensitive=True))
mcp.register_tool(MCPTool(name="powerbi_compliance", description="Gera dashboard Power BI de compliance", handler=_powerbi_compliance, parameters={"tenant_data": {"type": "string"}}))


class ToolCallRequest(BaseModel):
    tool: str
    params: dict = {}
    tenant_id: str = "default"


@erp_app.get("/health")
async def health():
    return {"status": "healthy", "server": mcp.server_id}


@erp_app.get("/mcp/manifest")
async def manifest():
    return mcp.manifest()


@erp_app.get("/mcp/tools")
async def list_tools():
    return {"tools": mcp.get_tools_list()}


@erp_app.post("/mcp/call")
async def call_tool(req: ToolCallRequest):
    result = await mcp.call_tool(req.tool, req.params, req.tenant_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
