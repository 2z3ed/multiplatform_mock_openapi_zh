from dataclasses import dataclass
from typing import Any


@dataclass
class ShipmentTraceDTO:
    time: str
    message: str
    location: str


@dataclass
class ShipmentItemDTO:
    shipment_id: str
    express_company: str
    express_no: str
    status: str
    status_name: str
    create_time: str | None
    estimated_arrival: str | None
    trace: list[ShipmentTraceDTO]


@dataclass
class ShipmentDTO:
    platform: str
    order_id: str
    shipments: list[ShipmentItemDTO]
    raw_json: dict[str, Any]