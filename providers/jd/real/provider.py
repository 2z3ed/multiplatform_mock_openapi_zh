"""Real JD provider placeholder - V1 skeleton for future extension.

V1 Real provider is NOT implemented yet.
This is a placeholder to satisfy the provider pattern requirement.

In V2/V3, this will be implemented to call actual JD APIs:
- https://api.jd.com/routerjson
- OAuth2 authentication
- Order/Logistics/After-sale APIs
"""

import os
from typing import Optional


class JdRealProvider:
    """Real JD provider - to be implemented in V2."""

    def __init__(self, app_key: Optional[str] = None, app_secret: Optional[str] = None):
        self.app_key = app_key or os.getenv("JD_APP_KEY", "")
        self.app_secret = app_secret or os.getenv("JD_APP_SECRET", "")
        self.access_token: Optional[str] = None
        self.base_url = "https://api.jd.com/routerjson"

    def get_platform(self) -> str:
        return "jd"

    def get_order(self, order_id: str) -> dict:
        """Get order from real JD API - not implemented in V1"""
        return {
            "error": "V1 real provider not implemented",
            "hint": "Use mock provider for V1",
            "order_id": order_id,
        }

    def get_shipment(self, order_id: str) -> dict:
        """Get shipment from real JD API - not implemented in V1"""
        return {
            "error": "V1 real provider not implemented",
            "hint": "Use mock provider for V1",
            "order_id": order_id,
        }

    def get_after_sale(self, after_sale_id: str) -> dict:
        """Get after-sale from real JD API - not implemented in V1"""
        return {
            "error": "V1 real provider not implemented",
            "hint": "Use mock provider for V1",
            "after_sale_id": after_sale_id,
        }


def get_provider() -> JdRealProvider:
    """Factory function to get real provider instance."""
    return JdRealProvider()