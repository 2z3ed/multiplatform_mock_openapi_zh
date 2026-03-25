"""Real WeCom KF provider placeholder - V1 skeleton for future extension.

V1 Real provider is NOT implemented yet.
This is a placeholder to satisfy the provider pattern requirement.

In V2/V3, this will be implemented to call actual WeCom APIs:
- https://qyapi.weixin.qq.com
- CorpID/Secret authentication
- Customer Service APIs
"""

import os
from typing import Optional


class WecomKfRealProvider:
    """Real WeCom KF provider - to be implemented in V2."""

    def __init__(self, corp_id: Optional[str] = None, corp_secret: Optional[str] = None):
        self.corp_id = corp_id or os.getenv("WECOM_CORP_ID", "")
        self.corp_secret = corp_secret or os.getenv("WECOM_CORP_SECRET", "")
        self.access_token: Optional[str] = None
        self.agent_id: Optional[str] = os.getenv("WECOM_AGENT_ID", "")

    def get_platform(self) -> str:
        return "wecom_kf"

    def get_token(self) -> dict:
        """Get access token from real WeCom API - not implemented in V1"""
        return {
            "error": "V1 real provider not implemented",
            "hint": "Use mock provider for V1",
        }

    def sync_message(self, msg_data: dict) -> dict:
        """Sync message from real WeCom API - not implemented in V1"""
        return {
            "error": "V1 real provider not implemented",
            "hint": "Use mock provider for V1",
        }

    def transfer_service(self, user_id: str, to_user: str) -> dict:
        """Transfer service state - not implemented in V1"""
        return {
            "error": "V1 real provider not implemented",
            "hint": "Use mock provider for V1",
        }


def get_provider() -> WecomKfRealProvider:
    """Factory function to get real provider instance."""
    return WecomKfRealProvider()