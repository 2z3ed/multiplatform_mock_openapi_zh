from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.risk_case import RiskCaseCreateRequest, RiskCaseResponse
from app.services.risk_case_service import RiskCaseService, InvalidStateTransitionError
from shared_db import get_db

router = APIRouter(prefix="/api/risk/cases", tags=["risk-cases"])


def get_risk_case_service(db: Session = Depends(get_db)) -> RiskCaseService:
    return RiskCaseService(db_session=db)


@router.post("", response_model=RiskCaseResponse, status_code=201)
def create_risk_case(
    req: RiskCaseCreateRequest,
    service: RiskCaseService = Depends(get_risk_case_service)
):
    result = service.create(
        conversation_id=req.conversation_id,
        customer_id=req.customer_id,
        risk_type=req.risk_type,
        severity=req.severity,
        evidence_json=req.evidence_json
    )
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to create risk case")
    return result


@router.get("", response_model=list[RiskCaseResponse])
def list_risk_cases(
    customer_id: int | None = None,
    service: RiskCaseService = Depends(get_risk_case_service)
):
    if customer_id:
        return service.list_by_customer(customer_id)
    return service.list_all()


@router.get("/{risk_case_id}", response_model=RiskCaseResponse)
def get_risk_case(
    risk_case_id: int,
    service: RiskCaseService = Depends(get_risk_case_service)
):
    result = service.get_by_id(risk_case_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Risk case not found")
    return result


@router.post("/{risk_case_id}/resolve", response_model=RiskCaseResponse)
def resolve_risk_case(
    risk_case_id: int,
    service: RiskCaseService = Depends(get_risk_case_service)
):
    try:
        result = service.resolve(risk_case_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Risk case not found")
        return result
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{risk_case_id}/dismiss", response_model=RiskCaseResponse)
def dismiss_risk_case(
    risk_case_id: int,
    service: RiskCaseService = Depends(get_risk_case_service)
):
    try:
        result = service.dismiss(risk_case_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Risk case not found")
        return result
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{risk_case_id}/escalate", response_model=RiskCaseResponse)
def escalate_risk_case(
    risk_case_id: int,
    service: RiskCaseService = Depends(get_risk_case_service)
):
    try:
        result = service.escalate(risk_case_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Risk case not found")
        return result
    except InvalidStateTransitionError as e:
        raise HTTPException(status_code=400, detail=str(e))
