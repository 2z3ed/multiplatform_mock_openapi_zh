import httpx
from provider_sdk.interfaces.order_provider import OrderProvider
from provider_sdk.interfaces.shipment_provider import ShipmentProvider
from provider_sdk.interfaces.after_sale_provider import AfterSaleProvider
from provider_sdk.dto.order_dto import OrderDTO
from provider_sdk.dto.shipment_dto import ShipmentDTO
from provider_sdk.dto.after_sale_dto import AfterSaleDTO
from providers.jd.mock.mapper import map_order, map_shipment, map_after_sale


class JdMockProvider(OrderProvider, ShipmentProvider, AfterSaleProvider):
    def __init__(self, base_url: str = "http://mock-platform-server:8004"):
        self.base_url = base_url

    def get_platform(self) -> str:
        return "jd"

    def get_order(self, order_id: str) -> OrderDTO:
        response = httpx.get(f"{self.base_url}/mock/jd/orders/{order_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return map_order(data, "jd")

    def get_shipment(self, order_id: str) -> ShipmentDTO:
        response = httpx.get(f"{self.base_url}/mock/jd/shipments/{order_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return map_shipment(data, "jd")

    def get_after_sale(self, after_sale_id: str) -> AfterSaleDTO:
        response = httpx.get(f"{self.base_url}/mock/jd/after-sales/{after_sale_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return map_after_sale(data, "jd")