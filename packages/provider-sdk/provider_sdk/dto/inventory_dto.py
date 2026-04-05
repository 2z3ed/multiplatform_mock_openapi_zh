from dataclasses import dataclass
from typing import Any


@dataclass
class InventoryItemDTO:
    sku_id: str
    product_id: str
    product_name: str
    stock_state: str
    quantity: int
    warehouse_name: str = ""


@dataclass
class InventoryDTO:
    platform: str
    order_id: str
    items: list[InventoryItemDTO]
    raw_json: dict[str, Any]
