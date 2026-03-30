from pydantic import BaseModel, Field
from typing import Optional


class QualityRuleCreateRequest(BaseModel):
    rule_code: str = Field(..., min_length=1, max_length=50)
    rule_name: str = Field(..., min_length=1, max_length=100)
    rule_type: str = Field(..., pattern="^(slow_reply|missed_response|forbidden_word)$")
    severity: str = Field(default="medium", pattern="^(low|medium|high)$")
    description: Optional[str] = None
    config_json: Optional[dict] = None


class QualityRuleResponse(BaseModel):
    id: int
    rule_code: str
    rule_name: str
    rule_type: str
    severity: str
    description: Optional[str] = None
    config_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
