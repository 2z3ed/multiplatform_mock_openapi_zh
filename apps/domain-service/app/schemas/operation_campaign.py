from typing import Optional

from pydantic import BaseModel


class OperationCampaignCreateRequest(BaseModel):
    name: str
    campaign_type: str
    target_description: Optional[str] = None
    audience_json: Optional[dict] = None
    preview_text: Optional[str] = None
    extra_json: Optional[dict] = None


class OperationCampaignUpdateRequest(BaseModel):
    name: Optional[str] = None
    campaign_type: Optional[str] = None
    target_description: Optional[str] = None
    audience_json: Optional[dict] = None
    preview_text: Optional[str] = None
    extra_json: Optional[dict] = None
    status: Optional[str] = None


class OperationCampaignResponse(BaseModel):
    id: int
    name: str
    campaign_type: str
    target_description: Optional[str] = None
    audience_json: Optional[dict] = None
    preview_text: Optional[str] = None
    status: str
    extra_json: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
