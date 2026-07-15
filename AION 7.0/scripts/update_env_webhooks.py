#!/usr/bin/env python3
"""Atualiza .env com os webhook secrets do Stripe"""
import os
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"

secrets = {
    "STRIPE_WEBHOOK_SECRET": "whsec_lh0FM0KRx2nISA6vJGcIr1WjnCze2r7U",
    "STRIPE_CONNECT_WEBHOOK_SECRET": "whsec_x5LDpemssxr1iH8SJpsgfeMra8yYPGse",
}

with open(env_path) as f:
    content = f.read()

for key, value in secrets.items():
    if key in content:
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith(key + "="):
                lines[i] = f"{key}={value}"
        content = "\n".join(lines)
    else:
        content += f"\n{key}={value}"

with open(env_path, "w") as f:
    f.write(content)

print("[OK] Webhook secrets adicionados ao .env")
