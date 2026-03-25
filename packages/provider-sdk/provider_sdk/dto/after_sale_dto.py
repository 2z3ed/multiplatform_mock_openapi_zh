from dataclasses import dataclass
from typing import Any


@dataclass
class AfterSaleDTO:
    platform: str
    after_sale_id: str
    order_id: str
    type: str
    type_name: str
    status: str
    status_name: str
    apply_time: str | None
    handle_time: str | None
    apply_amount: float
    approve_amount: float
    reason: str | None
    reason_detail: str | None
    raw_json: dict[str, Any]