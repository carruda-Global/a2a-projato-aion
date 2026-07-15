"""Public affiliate signup + link generation. Real commission tracking
lives in src/agents/affiliate_program.py, wired into the Stripe webhook."""
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from src.agents.affiliate_program import signup_affiliate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/affiliates", tags=["affiliates"])

_BASE_PAYMENT_LINKS = {
    "voice_receptionist_starter": "https://buy.stripe.com/28E4gBa6Ibov2PicOsg7e0x",
    "voice_receptionist_growth": "https://buy.stripe.com/aFa00l6UwdwDdtWeWAg7e0y",
    "voice_receptionist_agency": "https://buy.stripe.com/3cI9AVemYfEL2PibKog7e0z",
}


class SignupRequest(BaseModel):
    name: str
    email: EmailStr


@router.post("/signup")
async def affiliate_signup(request: SignupRequest):
    affiliate = await signup_affiliate(request.name, request.email)
    if affiliate is None:
        raise HTTPException(status_code=503, detail="Affiliate signup unavailable right now, try again shortly")
    code = affiliate["referral_code"]
    return {
        "referral_code": code,
        "commission_rate": "20% recurring for 12 months",
        "tracking_links": {plan: f"{url}?client_reference_id={code}" for plan, url in _BASE_PAYMENT_LINKS.items()},
    }
