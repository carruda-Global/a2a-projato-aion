"""
Script de setup do protocolo A2A (Agent-to-Agent) da Google.
Gera o Agent Card JSON e verifica a configuracao.

Uso:
    python scripts/setup_a2a_protocol.py
    python scripts/setup_a2a_protocol.py --base-url https://engenheiro-producao-ai.onrender.com
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from google.protobuf import json_format
from src.a2a_bridge.agent_cards import build_agent_card


def main():
    parser = argparse.ArgumentParser(description="Setup do Google A2A Protocol")
    parser.add_argument(
        "--base-url",
        default=os.getenv("A2A_BASE_URL", "http://localhost:8000"),
        help="URL base para os endpoints A2A",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Caminho para salvar o Agent Card JSON (opcional)",
    )
    args = parser.parse_args()

    card = build_agent_card(base_url=args.base_url)
    card_dict = json_format.MessageToDict(card)

    card_json = json.dumps(card_dict, ensure_ascii=False, indent=2)
    print("=== AGENT CARD ===")
    print(card_json)
    print()

    print("=== RESUMO ===")
    print(f"  Nome: {card.name}")
    print(f"  Skills: {len(card.skills)}")
    for s in card.skills:
        print(f"    - {s.id}: {s.name}")
    print(f"  Interfaces: {len(card.supported_interfaces)}")
    for iface in card.supported_interfaces:
        print(f"    - {iface.protocol_binding} v{iface.protocol_version}: {iface.url}")
    print(f"  Streaming: {card.capabilities.streaming}")
    print()

    print("=== ENDPOINTS A2A ===")
    print(f"  Agent Card:  {args.base_url}/.well-known/agent-card.json")
    print(f"  JSON-RPC:    {args.base_url}/a2a/jsonrpc")
    print(f"  REST:        {args.base_url}/a2a/rest")
    print()

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(card_json, encoding="utf-8")
        print(f"Agent Card salvo em: {output_path.resolve()}")


if __name__ == "__main__":
    main()
