"""Real Douyin Shop provider placeholder - V1 skeleton for future extension.

V1 Real provider is NOT implemented yet.
This is a placeholder to satisfy the provider pattern requirement.

In V2/V3, this will be implemented to call actual Douyin Shop APIs:
- https://open.douyin.com/api
- OAuth2 authentication
- Order/Refund/Product APIs
"""

import os
from typing import Optional


class DouyinShopRealProvider:
    """Real Douyin Shop provider - to be implemented in V2."""

    def __init__(self, app_key: Optional[str] = None, app_secret: Optional[str] = None):
        self.app_key = app_key or os.getenv("DOUYIN_APP_KEY", "")
        self.app_secret = app_secret or os.getenv("DOUYIN_APP_SECRET", "")
        self.access_token: Optional[str] = None

    def get_platform(self) -> str:
        return "douyin_shop"

    def get_order(self, order_id: str) -> dict:
        """Get order from real Douyin API - not implemented in V1"""
        return {
            "error": "V1 real provider not implemented",
            "hint": "Use mock provider for V1",
            "order_id": order_id,
        }

    def get_shipment(self, order_id: str) -> dict:
        """Douyin Shop doesn't have separate shipment API in V1"""
        return {
            "error": "V1 real provider not implemented",
            "hint": "Use mock provider for V1",
            "order_id": order_id,
        }

    def get_after_sale(self, after_sale_id: str) -> dict:
        """Get refund from real Douyin API - not implemented in V1"""
        return {
            "error": "V1 real provider not implemented",
            "hint": "Use mock provider for V1",
            "after_sale_id": after_sale_id,
        }


def get_provider() -> DouyinShopRealProvider:
    """Factory function to get real provider instance."""
    return DouyinShopRealProvider()