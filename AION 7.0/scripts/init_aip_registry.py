import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.security.aip_registry import AIPRegistry

REGISTRY_FILE = Path("credentials/aip_registry.json")


def init_registry():
    registry = AIPRegistry()
    keys_dir = Path("credentials/agents")
    registry_file = keys_dir / "registry.json"

    if not registry_file.exists():
        print("[!] Execute generate_agent_keys.py primeiro")
        return

    with open(registry_file) as f:
        agents = json.load(f)

    for agent in agents:
        public_key = bytes.fromhex(agent["public_key"])
        registry.register_agent(agent["agent_id"], f"Agent {agent['agent_id']}", "system", public_key)
        print(f"  [OK] {agent['agent_id']} registrado")

    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, "w") as f:
        json.dump({k: {kk: vv for kk, vv in v.items() if kk != "public_key"} for k, v in registry.agents.items()}, f, indent=2)
    print(f"\nRegistry salvo em {REGISTRY_FILE}")


if __name__ == "__main__":
    init_registry()
