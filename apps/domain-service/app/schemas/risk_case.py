from pydantic import BaseModel, Field
from typing import Optional


class RiskCaseCreateRequest(BaseModel):
    conversation_id: int
    customer_id: int
    risk_type: str = Field(..., pattern="^(complaint_tendency|negative_emotion|blacklisted_customer|other)$")
    severity: str = Field(default="medium", pattern="^(low|medium|high)$")
    evidence_json: Optional[dict] = None


class RiskCaseResponse(BaseModel):
    id: int
    conversation_id: int
    customer_id: int
    risk_type: str
    severity: str
    status: str
    evidence_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
