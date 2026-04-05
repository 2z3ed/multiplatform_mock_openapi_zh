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

    class Config:
        from_attributes = True


class AutoEvaluateRecommendationRequest(BaseModel):
    conversation_id: str
    customer_id: int
    order_timeout_hours: Optional[int] = 24
    after_sale_timeout_hours: Optional[int] = 48


class AutoEvaluateRecommendationResponse(BaseModel):
    created_recommendations: list[RecommendationResponse]
    skipped: int
