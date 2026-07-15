import asyncio
import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Ensure project root is on sys.path when running as script
if __name__ == "__main__" and not __package__:
    _root = Path(__file__).resolve().parent.parent.parent.parent
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("aion-linkedin-mcp")


async def main():
    parser = argparse.ArgumentParser(description="AION LinkedIn MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio",
                        help="MCP transport mode (default: stdio)")
    parser.add_argument("--port", type=int, default=9800,
                        help="Port for SSE mode (default: 9800)")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Host for SSE mode (default: 127.0.0.1)")
    parser.add_argument("--config", default=None,
                        help="Path to LinkedIn config YAML")
    args = parser.parse_args()

    from .config import LinkedInConfig
    from . import LinkedInIntegration

    config = LinkedInConfig()
    if args.config:
        import yaml
        cfg_path = Path(args.config)
        if cfg_path.exists():
            with open(cfg_path) as f:
                data = yaml.safe_load(f) or {}
            linkedin_data = data.get("linkedin", {})
            if linkedin_data.get("client_id"):
                config.client_id = linkedin_data["client_id"]
            if linkedin_data.get("client_secret"):
                config.client_secret = linkedin_data["client_secret"]
            if linkedin_data.get("redirect_uri"):
                config.redirect_uri = linkedin_data["redirect_uri"]

    if not config.is_configured:
        logger.warning("LinkedIn not configured. Set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET env vars.")
        logger.info("Starting in limited mode — tools will return auth errors until configured.")

    integration = LinkedInIntegration(config=config)
    await integration.initialize()

    mcp = integration.get_mcp_server()
    if args.transport == "stdio":
        logger.info("LinkedIn MCP server starting in stdio mode (JSON-RPC)")
        await mcp.run_stdio()
    elif args.transport == "sse":
        logger.info(f"LinkedIn MCP server starting in SSE mode on {args.host}:{args.port}")
        await mcp.run_sse(host=args.host, port=args.port)


if __name__ == "__main__":
    asyncio.run(main())
