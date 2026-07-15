from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class PrivacyConsent(BaseModel):
    user_id: str
    email: EmailStr
    consent_given: bool
    consent_version: str = "1.0"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    privacy_policy_accepted: bool = True
    terms_of_service_accepted: bool = True
    previous_versions: List[dict] = Field(default_factory=list)


class PrivacyRequest(BaseModel):
    user_id: str
    email: EmailStr
    request_type: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class PrivacyResponse(BaseModel):
    request_id: str
    user_id: str
    status: str
    message: str
    data: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)
