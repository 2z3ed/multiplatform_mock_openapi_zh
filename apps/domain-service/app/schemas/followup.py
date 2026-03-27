from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreateFollowUpTaskRequest(BaseModel):
    customer_id: int
    task_type: str
    title: str
    trigger_source: str = "manual"
    conversation_id: Optional[int] = None
    order_id: Optional[str] = None
    description: Optional[str] = None
    suggested_copy: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None
    extra_json: Optional[dict] = None


class UpdateFollowUpTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    suggested_copy: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    extra_json: Optional[dict] = None


class ExecuteFollowUpTaskRequest(BaseModel):
    completed_by: str


class CloseFollowUpTaskRequest(BaseModel):
    completed_by: str


class FollowUpTaskResponse(BaseModel):
    id: int
    conversation_id: Optional[int] = None
    customer_id: int
    order_id: Optional[str] = None
    task_type: str
    trigger_source: str
    title: str
    description: Optional[str] = None
    suggested_copy: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[str] = None
    completed_at: Optional[str] = None
    completed_by: Optional[str] = None
    extra_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class FollowUpTaskListResponse(BaseModel):
    items: list[FollowUpTaskResponse]
    total: int
    page: int
    size: int
