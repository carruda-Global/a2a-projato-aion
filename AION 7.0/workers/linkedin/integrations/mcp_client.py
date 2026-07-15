import json
import logging
import asyncio
import sys
from datetime import datetime
from .config import LinkedInConfig
from .oauth import LinkedInOAuth
from .tools import LinkedInTools

logger = logging.getLogger(__name__)


class MCPToolDefinition:
    def __init__(self, name: str, description: str, input_schema: dict, handler):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler


class LinkedInMCPServer:
    def __init__(self, config: LinkedInConfig, oauth: LinkedInOAuth):
        self.config = config
        self.oauth = oauth
        self.tools = LinkedInTools(config, oauth)
        self._tools_registry: dict[str, MCPToolDefinition] = {}
        self._register_tools()

    def _register_tools(self):
        tool_map = {
            "linkedin_get_profile": self.tools.get_profile,
            "linkedin_search_people": self.tools.search_people,
            "linkedin_search_companies": self.tools.search_companies,
            "linkedin_create_post": self.tools.create_post,
            "linkedin_get_post": self.tools.get_post,
            "linkedin_get_post_comments": self.tools.get_post_comments,
            "linkedin_create_comment": self.tools.create_comment,
            "linkedin_get_post_analytics": self.tools.get_post_analytics,
            "linkedin_get_company_profile": self.tools.get_company_profile,
        }
        for schema in self.tools.get_all_tools_schema():
            name = schema["name"]
            handler = tool_map.get(name)
            if handler:
                self._tools_registry[name] = MCPToolDefinition(
                    name=name,
                    description=schema["description"],
                    input_schema=schema["input_schema"],
                    handler=handler,
                )

    async def _handle_json_rpc(self, message: dict) -> dict:
        msg_id = message.get("id", 0)
        method = message.get("method", "")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {
                        "tools": {
                            "listChanged": False,
                        },
                        "resources": {},
                        "prompts": {},
                    },
                    "serverInfo": {
                        "name": "aion-linkedin-mcp",
                        "version": "1.0.0",
                    },
                },
            }

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": t.name,
                            "description": t.description,
                            "inputSchema": t.input_schema,
                        }
                        for t in self._tools_registry.values()
                    ]
                },
            }

        if method == "tools/call":
            tool_name = message.get("params", {}).get("name", "")
            arguments = message.get("params", {}).get("arguments", {})
            tool_def = self._tools_registry.get(tool_name)
            if not tool_def:
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"},
                }
            try:
                result = await tool_def.handler(**arguments)
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]},
                }
            except Exception as e:
                logger.exception(f"Tool {tool_name} failed")
                return {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32000, "message": str(e)},
                }

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }

    async def run_stdio(self):
        logger.info("LinkedIn MCP server starting in stdio mode")
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        writer_transport, writer_protocol = await loop.connect_write_pipe(
            lambda: asyncio.streams.FlowControlMixin(asyncio.get_event_loop()), sys.stdout
        )
        writer = asyncio.StreamWriter(writer_transport, writer_protocol, None, loop)

        while True:
            try:
                raw = await reader.readline()
                if not raw:
                    break
                line = raw.decode().strip()
                if not line:
                    continue
                if line.startswith("Content-Length:"):
                    content_length = int(line.split(":")[1].strip())
                    await reader.readline()
                    body = await reader.readexactly(content_length)
                    message = json.loads(body.decode())
                    response = await self._handle_json_rpc(message)
                    response_str = json.dumps(response)
                    writer.write(f"Content-Length: {len(response_str)}\r\n\r\n{response_str}".encode())
                    await writer.drain()
            except (asyncio.IncompleteReadError, ConnectionResetError):
                break
            except Exception as e:
                logger.exception(f"stdio error: {e}")
                break

    async def run_sse(self, host: str | None = None, port: int | None = None):
        from fastapi import FastAPI, Request
        from fastapi.responses import StreamingResponse
        import uvicorn

        app = FastAPI(title="AION LinkedIn MCP Server")

        @app.get("/sse")
        async def sse_endpoint(request: Request):
            async def event_stream():
                yield f"event: endpoint\ndata: /messages\n\n"
                yield f"event: connected\ndata: {json.dumps({'server': 'aion-linkedin-mcp', 'version': '1.0.0'})}\n\n"
                while True:
                    await asyncio.sleep(30)
                    yield f"event: heartbeat\ndata: {datetime.now().isoformat()}\n\n"

            return StreamingResponse(event_stream(), media_type="text/event-stream")

        @app.post("/messages")
        async def messages_endpoint(request: Request):
            body = await request.json()
            result = await self._handle_json_rpc(body)
            return result

        host = host or self.config.mcp_host
        port = port or self.config.mcp_port
        logger.info(f"LinkedIn MCP SSE server starting on {host}:{port}")
        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    def get_tools_registry(self) -> dict:
        return self._tools_registry

    async def call_tool(self, name: str, arguments: dict) -> dict:
        tool_def = self._tools_registry.get(name)
        if not tool_def:
            return {"error": f"Tool not found: {name}"}
        try:
            result = await tool_def.handler(**arguments)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}


import sys
