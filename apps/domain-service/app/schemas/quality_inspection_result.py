from pydantic import BaseModel
from typing import Optional


class QualityInspectionResultResponse(BaseModel):
    id: int
    conversation_id: int
    quality_rule_id: int
    hit: bool
    severity: str
    evidence_json: Optional[dict] = None
    inspected_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class QualityInspectRequest(BaseModel):
    conversation_id: int


class AutoEvaluateQualityRequest(BaseModel):
    conversation_id: str


class AutoEvaluateQualityResponse(BaseModel):
    created_results: list[QualityInspectionResultResponse]
    skipped: int
