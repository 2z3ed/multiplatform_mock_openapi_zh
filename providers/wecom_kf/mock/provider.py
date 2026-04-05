"""WeCom KF Mock Provider - connects to official-sim for order/shipment/after-sale data."""
import httpx
import os
from provider_sdk.interfaces.order_provider import OrderProvider
from provider_sdk.interfaces.shipment_provider import ShipmentProvider
from provider_sdk.interfaces.after_sale_provider import AfterSaleProvider
from provider_sdk.dto.order_dto import OrderDTO
from provider_sdk.dto.shipment_dto import ShipmentDTO
from provider_sdk.dto.after_sale_dto import AfterSaleDTO
from provider_sdk.dto.inventory_dto import InventoryDTO
from providers.wecom_kf.mock.platform_sim_adapter import (
    adapt_platform_sim_order,
    adapt_platform_sim_shipment,
    adapt_platform_sim_refund,
    adapt_platform_sim_inventory,
)
from providers.wecom_kf.mock.mapper import map_order, map_shipment, map_after_sale, map_inventory
from providers.utils.http_helper import _handle_response

OFFICIAL_SIM_URL = os.getenv("OFFICIAL_SIM_URL", "http://localhost:9001/official-sim/query")


class WecomKfMockProvider(OrderProvider, ShipmentProvider, AfterSaleProvider):
    def __init__(self, base_url: str = OFFICIAL_SIM_URL):
        self.base_url = base_url

    def get_platform(self) -> str:
        return "wecom_kf"

    def get_order(self, order_id: str) -> OrderDTO:
        response = httpx.get(
            f"{self.base_url}/orders/{order_id}",
            params={"platform": "wecom_kf"},
            timeout=10,
        )
        payload = _handle_response(response, "order", order_id, "wecom_kf")
        order_data = payload.get("data", {}).get("order", {})
        adapted = adapt_platform_sim_order(order_data)
        return map_order(adapted, "wecom_kf")

    def get_shipment(self, order_id: str) -> ShipmentDTO:
        response = httpx.get(
            f"{self.base_url}/orders/{order_id}/shipment",
            params={"platform": "wecom_kf"},
            timeout=10,
        )
        payload = _handle_response(response, "shipment", order_id, "wecom_kf")
        shipment_data = payload.get("data", {}).get("shipment", {})
        adapted = adapt_platform_sim_shipment(shipment_data, order_id)
        return map_shipment(adapted, "wecom_kf")

    def get_after_sale(self, after_sale_id: str) -> AfterSaleDTO:
        response = httpx.get(
            f"{self.base_url}/orders/{after_sale_id}/refund",
            params={"platform": "wecom_kf"},
            timeout=10,
        )
        payload = _handle_response(response, "after_sale", after_sale_id, "wecom_kf")
        refund_data = payload.get("data", {}).get("refund", {})
        adapted = adapt_platform_sim_refund(refund_data, after_sale_id)
        return map_after_sale(adapted, "wecom_kf")

    def get_inventory(self, order_id: str) -> InventoryDTO:
        response = httpx.get(
            f"{self.base_url}/orders/{order_id}/inventory",
            params={"platform": "wecom_kf"},
            timeout=10,
        )
        payload = _handle_response(response, "inventory", order_id, "wecom_kf")
        inventory_data = payload.get("data", {}).get("inventory", [])
        adapted = adapt_platform_sim_inventory(inventory_data, order_id)
        return map_inventory(adapted, "wecom_kf")
