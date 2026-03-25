import httpx
from provider_sdk.interfaces.order_provider import OrderProvider
from provider_sdk.interfaces.after_sale_provider import AfterSaleProvider
from provider_sdk.dto.order_dto import OrderDTO
from provider_sdk.dto.after_sale_dto import AfterSaleDTO
from providers.douyin_shop.mock.mapper import map_order, map_refund


class DouyinShopMockProvider(OrderProvider, AfterSaleProvider):
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url

    def get_platform(self) -> str:
        return "douyin_shop"

    def get_order(self, order_id: str) -> OrderDTO:
        response = httpx.get(f"{self.base_url}/mock/douyin-shop/orders/{order_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return map_order(data, "douyin_shop")

    def get_shipment(self, order_id: str):
        raise NotImplementedError("Douyin Shop does not have shipment API in V1")

    def get_after_sale(self, after_sale_id: str) -> AfterSaleDTO:
        response = httpx.get(f"{self.base_url}/mock/douyin-shop/refunds/{after_sale_id}", timeout=10)
        response.raise_for_status()
        data = response.json()
        return map_refund(data, "douyin_shop")