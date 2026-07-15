# google_marketplace/fulfillment_api.py
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from src.database.supabase_client import supabase
import jwt
import os

app = FastAPI()

class SubscriptionRequest(BaseModel):
    entitlement_id: str
    product_id: str
    plan_id: str
    customer_email: str

def verify_google_token(token: str) -> dict:
    """Valida token JWT do Google"""
    try:
        decoded = jwt.decode(
            token,
            options={"verify_signature": False},  # Em produção, verificar com chave pública Google
            audience=os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        )
        return decoded
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/google-marketplace/activate")
async def activate_subscription(request: Request, data: SubscriptionRequest):
    # 1. Valida token
    token = request.headers.get('Authorization')
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    
    payload = verify_google_token(token.replace('Bearer ', ''))
    
    # 2. Ativa no Supabase
    supabase.table('subscriptions').insert({
        'entitlement_id': data.entitlement_id,
        'product_id': data.product_id,
        'plan_id': data.plan_id,
        'customer_email': data.customer_email,
        'status': 'active',
        'source': 'google_marketplace',
        'activated_at': 'now()'
    }).execute()
    
    return {"status": "activated", "entitlement_id": data.entitlement_id}