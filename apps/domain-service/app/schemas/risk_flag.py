from typing import Optional

from pydantic import BaseModel


class RiskFlagCreateRequest(BaseModel):
    customer_id: int
    conversation_id: Optional[int] = None
    risk_type: str
    risk_level: Optional[str] = "low"
    description: Optional[str] = None
    extra_json: Optional[dict] = None


class RiskFlagResponse(BaseModel):
    id: int
    customer_id: int
    conversation_id: Optional[int] = None
    risk_type: str
    risk_level: str
    description: Optional[str] = None
    extra_json: Optional[dict] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class AutoEvaluateRiskRequest(BaseModel):
    conversation_id: str
    customer_id: int
    amount_threshold: Optional[int] = 5000


class AutoEvaluateRiskResponse(BaseModel):
    created_flags: list[RiskFlagResponse]
    skipped: int
