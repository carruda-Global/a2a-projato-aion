# oracle_marketplace/wind_automation.py
import subprocess
import json
import os

def create_oracle_listing():
    # 1. Cria arquivo de configuração
    config = {
        "display_name": "EcoSystem AEC - Regulatory Agents",
        "short_description": "21 agentes de IA para regularização, ESG, tributário e LGPD",
        "long_description": open('AGENTS.md', 'r').read()[:2000],
        "category": "AI_AGENTS_AND_TOOLS",
        "pricing": {
            "type": "PAYGO",
            "currencies": ["BRL"],
            "plans": [
                {"name": "Starter", "price": 997},
                {"name": "Professional", "price": 2391},
                {"name": "Enterprise", "price": 4685},
                {"name": "Full Suite", "price": 9497},
                {"name": "Compliance Pack", "price": 2391}
            ]
        }
    }
    
    with open('listing_config.yaml', 'w') as f:
        yaml.dump(config, f)
    
    # 2. Executa WIND CLI
    cmd = [
        'wind',
        'marketplace',
        'create-listing',
        '--config', 'listing_config.yaml'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"❌ Erro: {result.stderr}")
        return
    
    print("✅ Listagem criada no Oracle Cloud Marketplace")

if __name__ == '__main__':
    create_oracle_listing()