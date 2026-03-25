from dataclasses import dataclass
from typing import Any


@dataclass
class OrderItemDTO:
    sku_id: str
    sku_name: str
    quantity: int
    price: float
    sub_total: float


@dataclass
class AddressDTO:
    province: str
    city: str
    district: str
    detail: str


@dataclass
class OrderDTO:
    platform: str
    order_id: str
    status: str
    status_name: str
    create_time: str | None
    pay_time: str | None
    total_amount: float
    freight_amount: float
    discount_amount: float
    payment_amount: float
    buyer_nick: str | None
    buyer_phone: str | None
    receiver_name: str | None
    receiver_phone: str | None
    receiver_address: AddressDTO | None
    items: list[OrderItemDTO]
    raw_json: dict[str, Any]