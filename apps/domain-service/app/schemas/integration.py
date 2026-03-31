from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Literal


class InventorySnapshotCreateRequest(BaseModel):
    sku_code: str = Field(..., min_length=1, max_length=100)
    warehouse_code: str = Field(..., min_length=1, max_length=50)
    available_qty: int = Field(..., ge=0)
    reserved_qty: int = Field(default=0, ge=0)
    status: str = Field(default="normal", pattern="^(normal|low|out_of_stock)$")
    source_json: Optional[dict] = None
    snapshot_at: Optional[datetime] = None


class InventorySnapshotResponse(BaseModel):
    id: int
    sku_code: str
    warehouse_code: str
    available_qty: int
    reserved_qty: int
    status: str
    source_json: Optional[dict] = None
    snapshot_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class OrderAuditSnapshotCreateRequest(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(..., min_length=1, max_length=50)
    audit_status: str = Field(..., pattern="^(pending|approved|rejected)$")
    audit_reason: Optional[str] = Field(None, max_length=500)
    source_json: Optional[dict] = None
    snapshot_at: Optional[datetime] = None


class OrderAuditSnapshotResponse(BaseModel):
    id: int
    order_id: str
    platform: str
    audit_status: str
    audit_reason: Optional[str] = None
    source_json: Optional[dict] = None
    snapshot_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class OrderExceptionSnapshotCreateRequest(BaseModel):
    order_id: str = Field(..., min_length=1, max_length=100)
    platform: str = Field(..., min_length=1, max_length=50)
    exception_type: str = Field(..., pattern="^(delay|stockout|address|customs|other)$")
    exception_status: str = Field(..., pattern="^(open|processing|resolved|cancelled)$")
    detail_json: Optional[dict] = None
    snapshot_at: Optional[datetime] = None


class OrderExceptionSnapshotResponse(BaseModel):
    id: int
    order_id: str
    platform: str
    exception_type: str
    exception_status: str
    detail_json: Optional[dict] = None
    snapshot_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class ExplainStatusRequest(BaseModel):
    type: Literal["inventory", "audit", "exception"]
    sku_code: Optional[str] = Field(None, min_length=1, max_length=100)
    order_id: Optional[str] = Field(None, min_length=1, max_length=100)


class ExplainStatusResponse(BaseModel):
    explanation: str
    suggestion: str


class SyncStatusResponse(BaseModel):
    id: int
    trigger_type: str
    provider_mode: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    status: str
    error_summary: Optional[str] = None
    inventory_count: int
    audit_count: int
    exception_count: int

    class Config:
        from_attributes = True
