from typing import Optional

from pydantic import BaseModel


class CreateTagRequest(BaseModel):
    customer_id: int
    tag_type: str
    tag_value: str
    extra_json: Optional[dict] = None


class TagResponse(BaseModel):
    id: int
    customer_id: int
    tag_type: str
    tag_value: str
    source: str
    extra_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
