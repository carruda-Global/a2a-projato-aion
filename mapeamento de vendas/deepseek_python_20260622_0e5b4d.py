# google_marketplace/webhook_handler.py
from fastapi import FastAPI, Request, HTTPException
from src.database.supabase_client import supabase

app = FastAPI()

@app.post("/google-marketplace/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    event_type = data.get('eventType')
    entitlement_id = data.get('entitlementId')
    
    if event_type == 'ENTITLEMENT_CANCELLED':
        # Atualiza status para canceled
        supabase.table('subscriptions')\
            .update({'status': 'canceled'})\
            .eq('entitlement_id', entitlement_id)\
            .execute()
        print(f"❌ Assinatura {entitlement_id} cancelada")
    
    elif event_type == 'ENTITLEMENT_SUSPENDED':
        supabase.table('subscriptions')\
            .update({'status': 'suspended'})\
            .eq('entitlement_id', entitlement_id)\
            .execute()
        print(f"⏸️ Assinatura {entitlement_id} suspensa")
    
    elif event_type == 'ENTITLEMENT_RENEWED':
        supabase.table('subscriptions')\
            .update({'status': 'active', 'renewed_at': 'now()'})\
            .eq('entitlement_id', entitlement_id)\
            .execute()
        print(f"🔄 Assinatura {entitlement_id} renovada")
    
    return {"status": "ok"}