from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.profile import CreateProfileRequest, UpdateProfileRequest, ProfileResponse
from app.services.profile_service import CustomerProfileService
from shared_db import get_db

router = APIRouter(prefix="/api", tags=["customer-profile"])


def get_profile_service(db: Session = Depends(get_db)) -> CustomerProfileService:
    return CustomerProfileService(db_session=db)


@router.get("/customers/{customer_id}/profile", response_model=ProfileResponse)
def get_profile(
    customer_id: int,
    service: CustomerProfileService = Depends(get_profile_service)
):
    result = service.get_profile(customer_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result


@router.post("/profiles", response_model=ProfileResponse, status_code=201)
def create_profile(
    req: CreateProfileRequest,
    service: CustomerProfileService = Depends(get_profile_service)
):
    result = service.create_profile(
        customer_id=req.customer_id,
        total_orders=req.total_orders,
        total_spent=req.total_spent,
        avg_order_value=req.avg_order_value,
        extra_json=req.extra_json
    )
    if result is None:
        existing = service.get_profile(req.customer_id)
        if existing is not None:
            raise HTTPException(status_code=400, detail="Profile already exists")
        raise HTTPException(status_code=400, detail="Invalid total_orders or total_spent or avg_order_value")
    return result


@router.patch("/customers/{customer_id}/profile", response_model=ProfileResponse)
def update_profile(
    customer_id: int,
    req: UpdateProfileRequest,
    service: CustomerProfileService = Depends(get_profile_service)
):
    existing = service.get_profile(customer_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    updates = req.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    result = service.update_profile(customer_id, updates)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid field value")
    return result


@router.delete("/customers/{customer_id}/profile")
def delete_profile(
    customer_id: int,
    service: CustomerProfileService = Depends(get_profile_service)
):
    existing = service.get_profile(customer_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    success = service.delete_profile(customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"success": True}
