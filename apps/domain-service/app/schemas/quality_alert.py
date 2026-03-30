from pydantic import BaseModel
from typing import Optional


class QualityAlertResponse(BaseModel):
    id: int
    quality_inspection_result_id: int
    alert_level: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
