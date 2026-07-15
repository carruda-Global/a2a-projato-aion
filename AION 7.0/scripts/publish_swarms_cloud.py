import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.api.deepseek_client import DeepSeekClient
from src.agents import (
    SpecAnalystAgent,
    ProcurementAgent,
    InventoryAgent,
    LogisticsAgent,
    FieldExecutionAgent,
)

AGENTS = {
    "spec-analyst": {
        "cls": SpecAnalystAgent,
        "name": "Analisador de Especificações Técnicas",
        "description": "Analisa documentos técnicos de engenharia conforme normas NBR",
        "price_per_call": 0.50,
    },
    "procurement": {
        "cls": ProcurementAgent,
        "name": "Processador de Compras",
        "description": "Processa pedidos de materiais e compara cotações",
        "price_per_call": 0.50,
    },
    "inventory": {
        "cls": InventoryAgent,
        "name": "Gestor de Estoque",
        "description": "Monitora estoque e sugere reposições",
        "price_per_call": 0.30,
    },
    "logistics": {
        "cls": LogisticsAgent,
        "name": "Rastreador Logístico",
        "description": "Acompanha remessas e identifica problemas de entrega",
        "price_per_call": 0.30,
    },
    "field-execution": {
        "cls": FieldExecutionAgent,
        "name": "Executor de Campo",
        "description": "Gera instruções de execução a partir de plantas",
        "price_per_call": 0.70,
    },
}


def main():
    print("=" * 60)
    print("Publicando Agentes no Swarms Cloud")
    print("=" * 60)

    settings = Settings()
    errors = settings.validate()
    if errors:
        for err in errors:
            print(f"  [!] {err}")

    api_key = (
        os.getenv("SWARMS_CLOUD_API_KEY", "")
        or settings.config.get("swarms_cloud", {}).get("api_key", "")
    )

    if not api_key:
        print("[!] SWARMS_CLOUD_API_KEY não configurada. Pulando...")
        return

    try:
        from swarms_cloud.main import SwarmCloudAPI, AgentCreate
    except ImportError:
        print("[!] swarms-cloud não instalado. Execute: pip install swarms-cloud")
        return

    llm = DeepSeekClient(settings)

    with SwarmCloudAPI(api_key=api_key) as client:
        for agent_id, info in AGENTS.items():
            print(f"\nPublicando {info['name']}...")

            agent_instance = info["cls"](settings, llm)

            agent_code = f'''import httpx
from typing import Any

API_BASE = "{os.getenv('RENDER_URL', 'https://engenheiro-producao-ai.onrender.com')}/api/v1/agents/{agent_id}"

def main(request: dict, store: Any) -> dict:
    response = httpx.post(
        API_BASE,
        json=request.get("payload", {{}}),
        headers={{"X-API-Key": request.get("api_key", "")}},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()
'''

            agent_data = AgentCreate(
                name=info["name"],
                description=info["description"],
                code=agent_code,
                requirements="httpx",
                envs=f"API_KEY={settings.deepseek_api_key[:8]}...",
            )

            try:
                result = client.create_agent(agent_data)
                print(f"  [OK] ID: {result.id}")
            except Exception as e:
                print(f"  [ERR] {e}")

    print("\nConcluído! Agentes publicados no Swarms Cloud.")
    print("Acesse o dashboard em: https://swarms.world/platform")


if __name__ == "__main__":
    main()
