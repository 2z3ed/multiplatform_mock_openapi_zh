from pydantic import BaseModel


class JdTokenRequest(BaseModel):
    app_key: str | None = None
    app_secret: str | None = None
