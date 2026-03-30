from pydantic import BaseModel, Field
from typing import Optional


class BlacklistCustomerCreateRequest(BaseModel):
    customer_id: int
    reason: Optional[str] = None
    source: str = Field(default="manual", pattern="^(manual|system|complaint)$")


class BlacklistCustomerResponse(BaseModel):
    id: int
    customer_id: int
    reason: Optional[str] = None
    source: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
