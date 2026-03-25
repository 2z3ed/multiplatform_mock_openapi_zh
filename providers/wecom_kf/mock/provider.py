"""WeCom KF mock provider - V1 placeholder for message/customer service only."""


class WecomKfMockProvider:
    def get_platform(self) -> str:
        return "wecom_kf"

    def sync_message(self, msg_data: dict) -> dict:
        return {"status": "ok", "msgid": "mock_msg_id"}