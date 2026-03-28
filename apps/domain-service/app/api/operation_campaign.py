from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.operation_campaign import (
    OperationCampaignCreateRequest,
    OperationCampaignUpdateRequest,
    OperationCampaignResponse
)
from app.services.operation_campaign_service import OperationCampaignService
from shared_db import get_db

router = APIRouter(prefix="/api/operation-campaigns", tags=["operation-campaigns"])


def get_campaign_service(db: Session = Depends(get_db)) -> OperationCampaignService:
    return OperationCampaignService(db_session=db)


@router.post("", response_model=OperationCampaignResponse, status_code=201)
def create_campaign(
    req: OperationCampaignCreateRequest,
    service: OperationCampaignService = Depends(get_campaign_service)
):
    result = service.create_campaign(
        name=req.name,
        campaign_type=req.campaign_type,
        target_description=req.target_description,
        audience_json=req.audience_json,
        preview_text=req.preview_text,
        extra_json=req.extra_json
    )
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to create campaign")
    return result


@router.get("/{campaign_id}", response_model=OperationCampaignResponse)
def get_campaign(
    campaign_id: int,
    service: OperationCampaignService = Depends(get_campaign_service)
):
    result = service.get_campaign_by_id(campaign_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return result


@router.get("", response_model=list[OperationCampaignResponse])
def list_campaigns(
    service: OperationCampaignService = Depends(get_campaign_service)
):
    results = service.list_campaigns()
    return results


@router.patch("/{campaign_id}", response_model=OperationCampaignResponse)
def update_campaign(
    campaign_id: int,
    req: OperationCampaignUpdateRequest,
    service: OperationCampaignService = Depends(get_campaign_service)
):
    existing = service.get_campaign_by_id(campaign_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if existing["status"] != "draft":
        raise HTTPException(status_code=400, detail="Campaign is not in draft status")

    if "status" in req.model_dump(exclude_unset=True):
        raise HTTPException(status_code=400, detail="Cannot update status directly")

    updates = req.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    result = service.update_campaign(campaign_id, updates)
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to update campaign")
    return result


@router.post("/{campaign_id}/ready", response_model=OperationCampaignResponse)
def mark_campaign_ready(
    campaign_id: int,
    service: OperationCampaignService = Depends(get_campaign_service)
):
    existing = service.get_campaign_by_id(campaign_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if existing["status"] != "draft":
        raise HTTPException(status_code=400, detail="Campaign is not in draft status")

    result = service.mark_campaign_ready(campaign_id)
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to mark campaign ready")
    return result


@router.post("/{campaign_id}/complete", response_model=OperationCampaignResponse)
def complete_campaign(
    campaign_id: int,
    service: OperationCampaignService = Depends(get_campaign_service)
):
    existing = service.get_campaign_by_id(campaign_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if existing["status"] != "ready":
        raise HTTPException(status_code=400, detail="Campaign is not in ready status")

    result = service.complete_campaign(campaign_id)
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to complete campaign")
    return result


@router.post("/{campaign_id}/cancel", response_model=OperationCampaignResponse)
def cancel_campaign(
    campaign_id: int,
    service: OperationCampaignService = Depends(get_campaign_service)
):
    existing = service.get_campaign_by_id(campaign_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if existing["status"] == "completed":
        raise HTTPException(status_code=400, detail="Cannot cancel completed campaign")

    result = service.cancel_campaign(campaign_id)
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to cancel campaign")
    return result
