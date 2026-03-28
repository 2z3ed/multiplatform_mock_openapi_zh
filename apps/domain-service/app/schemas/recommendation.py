from typing import Optional

from pydantic import BaseModel


class RecommendationCreateRequest(BaseModel):
    conversation_id: int
    customer_id: int
    product_id: str
    product_name: str
    reason: Optional[str] = None
    suggested_copy: Optional[str] = None
    extra_json: Optional[dict] = None


class RecommendationResponse(BaseModel):
    id: int
    conversation_id: int
    customer_id: int
    product_id: str
    product_name: str
    reason: Optional[str] = None
    suggested_copy: Optional[str] = None
    status: str
    extra_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
