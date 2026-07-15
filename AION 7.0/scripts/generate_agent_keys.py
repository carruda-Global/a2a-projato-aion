import os
import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, PublicFormat

AGENTS = ["#1","#2","#3","#4","#5","#6","#7","#8","#9","#10","#11","#12","#13","#14","#15","#16","#17","#18","#19","#20","#21","#22","#23","#24","#25","#26","#27","#N1","#N2","#N3","#31","#32","#33","#34","#35","#36","#37","#38","#39","#40","#41","#42","#43","#44","#45","#46","#47","#48","#49","#50","#51","#52","#53","#54","#55","#56","#57","#58","#59"] + [f"M{i}" for i in range(1,16)]


def generate_keys_for_agents():
    keys_dir = Path("credentials/agents")
    keys_dir.mkdir(parents=True, exist_ok=True)

    registry = []
    for agent_id in AGENTS:
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        with open(keys_dir / f"{agent_id}.key", "wb") as f:
            f.write(private_key.private_bytes(encoding=Encoding.Raw, format=PrivateFormat.Raw))
        with open(keys_dir / f"{agent_id}.pub", "wb") as f:
            f.write(public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw))

        registry.append({"agent_id": agent_id, "public_key": public_key.public_bytes(encoding=Encoding.Raw, format=PublicFormat.Raw).hex()})
        print(f"OK Chaves geradas para agente {agent_id}")

    with open(keys_dir / "registry.json", "w") as f:
        json.dump(registry, f, indent=2)
    print(f"Registry salvo em {keys_dir / 'registry.json'}")


if __name__ == "__main__":
    generate_keys_for_agents()
