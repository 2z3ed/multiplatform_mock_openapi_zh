from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.risk_flag import (
    RiskFlagCreateRequest,
    RiskFlagResponse,
    AutoEvaluateRiskRequest,
    AutoEvaluateRiskResponse,
)
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


@router.post("/auto-evaluate", response_model=AutoEvaluateRiskResponse)
def auto_evaluate_risk(
    req: AutoEvaluateRiskRequest,
    db: Session = Depends(get_db),
    service: RiskFlagService = Depends(get_risk_flag_service),
):
    from app.services.context_aggregation_service import aggregate_conversation_context
    from app.services.risk_rule_service import evaluate_conversation_for_risk

    try:
        conv_id = int(req.conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid conversation_id")

    context = aggregate_conversation_context(db, conv_id)

    flag_payloads = evaluate_conversation_for_risk(
        conversation_context=context,
        conversation_id=conv_id,
        customer_id=req.customer_id,
        amount_threshold=req.amount_threshold or 5000,
    )

    created = []
    skipped = 0
    for payload in flag_payloads:
        existing_flags = service.list_risk_flags_by_customer_id(payload["customer_id"])
        duplicate = any(
            f["risk_type"] == payload["risk_type"]
            and f["status"] == "active"
            and f.get("extra_json", {}).get("rule") == payload.get("extra_json", {}).get("rule")
            and f.get("extra_json", {}).get("order_id") == payload.get("extra_json", {}).get("order_id")
            and f.get("extra_json", {}).get("sku_id") == payload.get("extra_json", {}).get("sku_id")
            for f in existing_flags
        )
        if duplicate:
            skipped += 1
            continue

        result = service.create_risk_flag(
            customer_id=payload["customer_id"],
            risk_type=payload["risk_type"],
            conversation_id=payload.get("conversation_id"),
            risk_level=payload.get("risk_level", "low"),
            description=payload.get("description"),
            extra_json=payload.get("extra_json"),
        )
        if result:
            created.append(result)
        else:
            skipped += 1

    return {
        "created_flags": created,
        "skipped": skipped,
    }
