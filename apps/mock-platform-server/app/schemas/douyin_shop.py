from pydantic import BaseModel


class DouyinTokenRequest(BaseModel):
    app_id: str | None = None
    app_secret: str | None = None
