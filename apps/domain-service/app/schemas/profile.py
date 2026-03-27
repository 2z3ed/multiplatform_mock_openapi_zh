from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class CreateProfileRequest(BaseModel):
    customer_id: int
    total_orders: int = 0
    total_spent: Decimal = Decimal("0.00")
    avg_order_value: Decimal = Decimal("0.00")
    extra_json: Optional[dict] = None


class UpdateProfileRequest(BaseModel):
    total_orders: Optional[int] = None
    total_spent: Optional[Decimal] = None
    avg_order_value: Optional[Decimal] = None
    extra_json: Optional[dict] = None


class ProfileResponse(BaseModel):
    id: int
    customer_id: int
    total_orders: int
    total_spent: str
    avg_order_value: str
    extra_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
