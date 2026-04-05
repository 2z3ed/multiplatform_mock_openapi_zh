import httpx
import os
from provider_sdk.interfaces.order_provider import OrderProvider
from provider_sdk.interfaces.shipment_provider import ShipmentProvider
from provider_sdk.interfaces.after_sale_provider import AfterSaleProvider
from provider_sdk.dto.order_dto import OrderDTO
from provider_sdk.dto.shipment_dto import ShipmentDTO
from provider_sdk.dto.after_sale_dto import AfterSaleDTO
from provider_sdk.dto.inventory_dto import InventoryDTO
from providers.jd.mock.mapper import map_order, map_shipment, map_after_sale, map_inventory
from providers.jd.mock.platform_sim_adapter import (
    adapt_platform_sim_order,
    adapt_platform_sim_shipment,
    adapt_platform_sim_refund,
    adapt_platform_sim_inventory,
)
from providers.utils.http_helper import _handle_response

OFFICIAL_SIM_URL = os.getenv("OFFICIAL_SIM_URL", "http://localhost:9001/official-sim/query")


class JdMockProvider(OrderProvider, ShipmentProvider, AfterSaleProvider):
    def __init__(self, base_url: str = OFFICIAL_SIM_URL):
        self.base_url = base_url

    def get_platform(self) -> str:
        return "jd"

    def get_order(self, order_id: str) -> OrderDTO:
        response = httpx.get(
            f"{self.base_url}/orders/{order_id}",
            params={"platform": "jd"},
            timeout=10,
        )
        payload = _handle_response(response, "order", order_id, "jd")
        order_data = payload.get("data", {}).get("order", {})
        adapted = adapt_platform_sim_order(order_data)
        return map_order(adapted, "jd")

    def get_shipment(self, order_id: str) -> ShipmentDTO:
        response = httpx.get(
            f"{self.base_url}/orders/{order_id}/shipment",
            params={"platform": "jd"},
            timeout=10,
        )
        payload = _handle_response(response, "shipment", order_id, "jd")
        shipment_data = payload.get("data", {}).get("shipment", {})
        adapted = adapt_platform_sim_shipment(shipment_data, order_id)
        return map_shipment(adapted, "jd")

    def get_after_sale(self, after_sale_id: str) -> AfterSaleDTO:
        order_id = after_sale_id.replace("REFUND_", "") if after_sale_id.startswith("REFUND_") else after_sale_id
        response = httpx.get(
            f"{self.base_url}/orders/{order_id}/refund",
            params={"platform": "jd"},
            timeout=10,
        )
        payload = _handle_response(response, "after_sale", order_id, "jd")
        refund_data = payload.get("data", {}).get("refund", {})
        adapted = adapt_platform_sim_refund(refund_data, order_id)
        return map_after_sale(adapted, "jd")

    def get_inventory(self, order_id: str) -> InventoryDTO:
        response = httpx.get(
            f"{self.base_url}/orders/{order_id}/inventory",
            params={"platform": "jd"},
            timeout=10,
        )
        payload = _handle_response(response, "inventory", order_id, "jd")
        inventory_data = payload.get("data", {}).get("inventory", [])
        adapted = adapt_platform_sim_inventory(inventory_data, order_id)
        return map_inventory(adapted, "jd")
