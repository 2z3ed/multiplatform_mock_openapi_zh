from typing import Optional

from pydantic import BaseModel


class AnalyticsSummarizeRequest(BaseModel):
    stat_date: str


class AnalyticsSummaryResponse(BaseModel):
    id: int
    stat_date: str
    recommendation_created_count: int
    recommendation_accepted_count: int
    followup_executed_count: int
    followup_closed_count: int
    operation_campaign_completed_count: int
    extra_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
