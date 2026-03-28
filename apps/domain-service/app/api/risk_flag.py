from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.risk_flag import RiskFlagCreateRequest, RiskFlagResponse
from app.services.risk_flag_service import RiskFlagService
from shared_db import get_db

router = APIRouter(prefix="/api/risk-flags", tags=["risk-flags"])


def get_risk_flag_service(db: Session = Depends(get_db)) -> RiskFlagService:
    return RiskFlagService(db_session=db)


@router.post("", response_model=RiskFlagResponse, status_code=201)
def create_risk_flag(
    req: RiskFlagCreateRequest,
    service: RiskFlagService = Depends(get_risk_flag_service)
):
    result = service.create_risk_flag(
        customer_id=req.customer_id,
        risk_type=req.risk_type,
        conversation_id=req.conversation_id,
        risk_level=req.risk_level or "low",
        description=req.description,
        extra_json=req.extra_json,
    )
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to create risk flag")
    return result


@router.get("/{risk_flag_id}", response_model=RiskFlagResponse)
def get_risk_flag(
    risk_flag_id: int,
    service: RiskFlagService = Depends(get_risk_flag_service)
):
    result = service.get_risk_flag_by_id(risk_flag_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Risk flag not found")
    return result


@router.get("", response_model=list[RiskFlagResponse])
def list_risk_flags(
    customer_id: int = Query(..., description="Customer ID"),
    service: RiskFlagService = Depends(get_risk_flag_service)
):
    results = service.list_risk_flags_by_customer_id(customer_id)
    return results


@router.post("/{risk_flag_id}/resolve", response_model=RiskFlagResponse)
def resolve_risk_flag(
    risk_flag_id: int,
    service: RiskFlagService = Depends(get_risk_flag_service)
):
    result, error = service.resolve_risk_flag(risk_flag_id)
    if error == "not_found":
        raise HTTPException(status_code=404, detail="Risk flag not found")
    if error == "not_active":
        raise HTTPException(status_code=400, detail="Risk flag is not in active status")
    return result


@router.post("/{risk_flag_id}/dismiss", response_model=RiskFlagResponse)
def dismiss_risk_flag(
    risk_flag_id: int,
    service: RiskFlagService = Depends(get_risk_flag_service)
):
    result, error = service.dismiss_risk_flag(risk_flag_id)
    if error == "not_found":
        raise HTTPException(status_code=404, detail="Risk flag not found")
    if error == "not_active":
        raise HTTPException(status_code=400, detail="Risk flag is not in active status")
    return result
