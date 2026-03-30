from datetime import date
from pydantic import BaseModel, Field
from typing import Optional, Literal


class VOCTopicCreateRequest(BaseModel):
    topic_name: str = Field(..., min_length=1, max_length=200)
    topic_type: str = Field(..., pattern="^(complaint|feedback|suggestion|other)$")
    source: str = Field(..., pattern="^(conversation|survey|other)$")
    occurrence_count: int = Field(default=0, ge=0)
    summary: Optional[str] = None
    extra_json: Optional[dict] = None


class VOCTopicResponse(BaseModel):
    id: int
    topic_name: str
    topic_type: str
    source: str
    occurrence_count: int
    summary: Optional[str] = None
    extra_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class TrainingCaseCreateRequest(BaseModel):
    case_title: str = Field(..., min_length=1, max_length=200)
    case_type: str = Field(..., pattern="^(good|bad|typical|edge_case)$")
    conversation_id: Optional[int] = None
    customer_id: Optional[int] = None
    case_summary: Optional[str] = None
    source_json: Optional[dict] = None


class TrainingCaseResponse(BaseModel):
    id: int
    conversation_id: Optional[int] = None
    customer_id: Optional[int] = None
    case_title: str
    case_summary: Optional[str] = None
    case_type: str
    source_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class TrainingTaskCreateRequest(BaseModel):
    task_name: str = Field(..., min_length=1, max_length=200)
    task_type: str = Field(..., pattern="^(review|practice|quiz|other)$")
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed|cancelled)$")
    related_case_id: Optional[int] = None
    detail_json: Optional[dict] = None


class TrainingTaskResponse(BaseModel):
    id: int
    task_name: str
    task_type: str
    status: str
    related_case_id: Optional[int] = None
    detail_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class DashboardSnapshotCreateRequest(BaseModel):
    snapshot_date: date
    metric_type: str = Field(..., pattern="^(conversation_count|avg_response_time|satisfaction_score|resolved_case_count)$")
    metric_value: float = Field(..., ge=0)
    detail_json: Optional[dict] = None


class DashboardSnapshotResponse(BaseModel):
    id: int
    snapshot_date: str
    metric_type: str
    metric_value: float
    detail_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
