from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import os
import subprocess

out_dir = os.path.dirname(os.path.abspath(__file__))
pfx_path = os.path.join(out_dir, "server.pfx")
jks_path = os.path.join(out_dir, "server.jks")

# Try using keytool (Java) to convert PFX to JKS
try:
    result = subprocess.run(
        ["keytool", "-importkeystore",
         "-srckeystore", pfx_path,
         "-srcstoretype", "PKCS12",
         "-srcstorepass", "globalmatch2026",
         "-destkeystore", jks_path,
         "-deststoretype", "JKS",
         "-deststorepass", "globalmatch2026",
         "-alias", "1"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        print(f"JKS gerado: {jks_path}")
        print("Senha: globalmatch2026")
    else:
        print("Erro keytool:", result.stderr)
        print("Tente com o PFX diretamente selecionando PKCS12 no Salesforce")
except FileNotFoundError:
    print("keytool não encontrado. Use o PFX e selecione PKCS12 no Salesforce")
    print(f"PFX: {pfx_path}")
    print("Senha: globalmatch2026")
