from pydantic import BaseModel


class WecomTokenRequest(BaseModel):
    corp_id: str | None = None
    secret: str | None = None
