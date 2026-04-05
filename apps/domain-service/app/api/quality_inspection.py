from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.quality_inspection_result import (
    QualityInspectRequest,
    QualityInspectionResultResponse,
    AutoEvaluateQualityRequest,
    AutoEvaluateQualityResponse,
)
from app.services.quality_inspection_service import QualityInspectionService
from shared_db import get_db

router = APIRouter(prefix="/api/quality", tags=["quality-inspection"])


def get_quality_inspection_service(db: Session = Depends(get_db)) -> QualityInspectionService:
    return QualityInspectionService(db_session=db)


@router.post("/inspect", response_model=list[QualityInspectionResultResponse], status_code=200)
def inspect_conversation(
    req: QualityInspectRequest,
    service: QualityInspectionService = Depends(get_quality_inspection_service)
):
    return service.inspect_conversation(req.conversation_id)


@router.get("/results", response_model=list[QualityInspectionResultResponse])
def list_results(
    conversation_id: int | None = None,
    service: QualityInspectionService = Depends(get_quality_inspection_service)
):
    if conversation_id:
        return service.list_by_conversation(conversation_id)
    return service.list_all()


@router.get("/results/{result_id}", response_model=QualityInspectionResultResponse)
def get_result(
    result_id: int,
    service: QualityInspectionService = Depends(get_quality_inspection_service)
):
    result = service.get_by_id(result_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Quality inspection result not found")
    return result


@router.post("/auto-evaluate", response_model=AutoEvaluateQualityResponse)
def auto_evaluate_quality(
    req: AutoEvaluateQualityRequest,
    db: Session = Depends(get_db),
    service: QualityInspectionService = Depends(get_quality_inspection_service),
):
    from app.services.context_aggregation_service import aggregate_conversation_context
    from app.services.explain_service import explain_from_context
    from app.services.quality_rule_service import evaluate_conversation_for_quality

    try:
        conv_id = int(req.conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid conversation_id")

    context = aggregate_conversation_context(db, conv_id)
    explain_result = explain_from_context(context)

    payloads = evaluate_conversation_for_quality(
        conversation_context=context,
        explain_result=explain_result,
        conversation_id=conv_id,
    )

    created = []
    skipped = 0
    for payload in payloads:
        rule = service._rule_repo.get_by_rule_code(payload["rule_code"])
        if rule is None:
            rule = service._rule_repo.create(
                rule_code=payload["rule_code"],
                rule_name=payload["rule_name"],
                rule_type=payload["rule_type"],
                severity=payload["severity"],
                description=payload.get("rule_description"),
                config_json=payload.get("rule_config"),
            )

        existing = service.list_by_conversation(conv_id)
        duplicate = any(
            r["quality_rule_id"] == rule.id and r["hit"]
            for r in existing
        )
        if duplicate:
            skipped += 1
            continue

        result = service._result_repo.create(
            conversation_id=conv_id,
            quality_rule_id=rule.id,
            hit=True,
            severity=payload["severity"],
            evidence_json=payload.get("evidence_json"),
        )
        created.append(service._to_dict(result))

    return {
        "created_results": created,
        "skipped": skipped,
    }
