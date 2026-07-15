from typing import Any, Callable
from pydantic import BaseModel

class MCPTool(BaseModel):
    name: str
    description: str
    handler: Callable[..., dict] = None
    parameters: dict = {}
    sensitive: bool = False

class MCPServer:
    def __init__(self, server_id: str, name: str, description: str):
        self.server_id = server_id
        self.name = name
        self.description = description
        self.tools: dict[str, MCPTool] = {}
        self.llm_routing: dict[str, str] = {}

    def register_tool(self, tool: MCPTool):
        self.tools[tool.name] = tool

    def get_tools_list(self) -> list[dict]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
                "sensitive": t.sensitive,
            }
            for t in self.tools.values()
        ]

    async def call_tool(self, tool_name: str, params: dict[str, Any], tenant_id: str = "default") -> dict:
        tool = self.tools.get(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        if tool.handler:
            return tool.handler(**params)
        return {"error": "Tool handler not implemented"}

    def manifest(self) -> dict:
        return {
            "id": self.server_id,
            "name": self.name,
            "description": self.description,
            "tools": self.get_tools_list(),
        }
