# google_marketplace/create_offer.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json

def create_google_offer():
    credentials = service_account.Credentials.from_service_account_file(
        os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
        scopes=['https://www.googleapis.com/auth/cloud-platform']
    )
    service = build('cloudbilling', 'v1', credentials=credentials)
    
    # Carrega descrição do AGENTS.md
    with open('AGENTS.md', 'r') as f:
        description = f.read()[:500]  # Resumo
    
    offer = {
        'name': 'EcoSystem AEC - Regulatory Agents',
        'description': description,
        'category': 'AI_AGENTS_AND_TOOLS',
        'pricing': {
            'starter': {'price': 997, 'currency': 'BRL'},
            'professional': {'price': 2391, 'currency': 'BRL'},
            'enterprise': {'price': 4685, 'currency': 'BRL'},
            'full_suite': {'price': 9497, 'currency': 'BRL'},
            'compliance_pack': {'price': 2391, 'currency': 'BRL'},
        }
    }
    
    response = service.projects().createOffer(
        parent=f'projects/{os.getenv("GOOGLE_CLOUD_PROJECT_ID")}',
        body=offer
    ).execute()
    
    print(f"✅ Oferta criada: {response['name']}")

if __name__ == '__main__':
    create_google_offer()