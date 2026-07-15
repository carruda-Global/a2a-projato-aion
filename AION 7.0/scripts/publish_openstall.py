import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import Settings

AGENT_CAPABILITIES = [
    {
        "name": "analisador-especificacoes",
        "title": "Analisador de Especificações Técnicas",
        "description": "Analisa documentos técnicos de engenharia, extraindo requisitos e apontando inconsistências com normas NBR.",
        "category": "engineering",
        "tags": "AEC,engenharia,especificações,normas,NBR",
        "price": 500,
    },
    {
        "name": "processador-compras",
        "title": "Processador de Ordens de Compra",
        "description": "Processa pedidos de materiais, compara cotações de fornecedores e otimiza aquisições para obras.",
        "category": "procurement",
        "tags": "AEC,compras,cotações,materiais",
        "price": 500,
    },
    {
        "name": "gestor-estoque",
        "title": "Gestor de Estoque de Obra",
        "description": "Monitora níveis de estoque, sugere reposições e indica materiais substitutos quando necessário.",
        "category": "inventory",
        "tags": "AEC,estoque,materiais,reposição",
        "price": 300,
    },
    {
        "name": "rastreador-logistico",
        "title": "Rastreador Logístico de Materiais",
        "description": "Acompanha remessas de materiais, identifica atrasos e problemas de entrega em tempo real.",
        "category": "logistics",
        "tags": "AEC,logística,entregas,rastreamento",
        "price": 300,
    },
    {
        "name": "executor-campo",
        "title": "Gerador de Instruções de Execução",
        "description": "Gera instruções passo a passo para execução em campo a partir de plantas e memoriais descritivos.",
        "category": "engineering",
        "tags": "AEC,execução,obra,instruções,campo",
        "price": 700,
    },
]


def check_openstall_installed() -> bool:
    try:
        subprocess.run(["npx", "@openstall/sdk", "--version"], capture_output=True, check=False)
        return True
    except FileNotFoundError:
        return False


def install_openstall():
    print("Instalando OpenStall SDK...")
    subprocess.run(["npm", "install", "-g", "@openstall/sdk"], check=True)


def register_agent(name: str):
    print(f"Registrando agente no OpenStall: {name}")
    subprocess.run(
        ["npx", "@openstall/sdk", "register", "--name", name, "--owner", "engenheiro-producao-ai"],
        check=True,
    )


def publish_capability(cap: dict):
    print(f"Publicando capacidade: {cap['title']}")
    subprocess.run(
        [
            "npx", "@openstall/sdk", "publish",
            "--name", cap["name"],
            "--title", cap["title"],
            "--description", cap["description"],
            "--price", str(cap["price"]),
            "--category", cap["category"],
            "--tags", cap["tags"],
        ],
        check=True,
    )


def main():
    print("=" * 60)
    print("Publicando Agentes no OpenStall Marketplace")
    print("=" * 60)

    settings = Settings()
    errors = settings.validate()
    if errors:
        for err in errors:
            print(f"  [!] {err}")

    if not check_openstall_installed():
        install_openstall()

    register_agent("EngenheiroProducaoAI")

    for cap in AGENT_CAPABILITIES:
        publish_capability(cap)

    print("\nConcluído! Agentes publicados no OpenStall:")
    for cap in AGENT_CAPABILITIES:
        print(f"  - {cap['title']} ({cap['price']} créditos)")

    print("\nPróximos passos:")
    print("  1. Verifique seu saldo: openstall balance")
    print("  2. Teste uma capacidade: openstall discover engineering")
    print("  3. Acompanhe em: https://openstall.ai")


if __name__ == "__main__":
    main()
