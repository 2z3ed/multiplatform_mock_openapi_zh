from pydantic import BaseModel


class NotImplementedResponse(BaseModel):
    detail: str = "Round 1 skeleton: endpoint not implemented"
