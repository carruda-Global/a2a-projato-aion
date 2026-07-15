from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
import os

out_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(out_dir, "server.key"), "rb") as f:
    key = serialization.load_pem_private_key(f.read(), password=None)

with open(os.path.join(out_dir, "server.crt"), "rb") as f:
    cert = x509.load_pem_x509_certificate(f.read())

password = b"globalmatch2026"

pfx_data = pkcs12.serialize_key_and_certificates(
    name=b"EcoSystemAEC",
    key=key,
    cert=cert,
    cas=None,
    encryption_algorithm=serialization.BestAvailableEncryption(password),
)

pfx_path = os.path.join(out_dir, "server.pfx")
with open(pfx_path, "wb") as f:
    f.write(pfx_data)

print(f"PFX gerado: {pfx_path}")
print(f"Senha do PFX: globalmatch2026")
