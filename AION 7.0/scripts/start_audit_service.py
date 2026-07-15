import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.security.audit import AuditChain


def start_audit_service():
    audit = AuditChain()
    print("[OK] Servico de auditoria iniciado")
    print("  Merkle Chain: AuditChain")
    print("  Status: aguardando entradas...\n")

    # Demo
    audit.append({"agent_id": "#1", "action": "execute", "resource": "spec_analyst", "status": "success"})
    audit.append({"agent_id": "#13", "action": "execute", "resource": "nr1_psicossocial", "status": "success"})
    audit.append({"agent_id": "#49", "action": "orchestrate", "resource": "full_pipeline", "status": "success"})

    print(f"  Entradas na cadeia: {len(audit.chain)}")
    print(f"  Merkle Root: {audit.merkle_root}")
    print(f"  Cadeia valida: {audit.verify()}")
    print(f"  Prova bloco 0: {audit.get_proof(0) is not None}")


if __name__ == "__main__":
    start_audit_service()
