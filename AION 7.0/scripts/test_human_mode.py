import os, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()
from src.api.deepseek_client import DeepSeekClient
from src.config import Settings
from src.agents.outbound_sdr_agent import SYSTEM_PROMPT_HUMAN

settings = Settings()
ds = DeepSeekClient(settings)

tests = [
    {"empresa": "Construtora Alvorada", "cargo": "Engenheiro de Seguranca", "motivo": "180 funcionarios sem PGR"},
    {"empresa": "MRV Engenharia", "cargo": "Diretor Juridico", "motivo": "LGPD em obras"},
    {"empresa": "Hospital Albert Einstein", "cargo": "CEO", "motivo": "dados sensiveis de pacientes"},
]

for t in tests:
    prompt = f"Empresa: {t['empresa']}\nCargo: {t['cargo']}\nMotivo: {t['motivo']}\nEscreva msg WhatsApp curta e natural em portugues brasileiro informal"
    result = ds.chat(SYSTEM_PROMPT_HUMAN, prompt)
    print(f"--- {t['empresa']} ---")
    print(result[:250])
    print()
