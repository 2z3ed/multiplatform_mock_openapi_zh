from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.quality_rule import QualityRuleCreateRequest, QualityRuleResponse
from app.services.quality_rule_service import QualityRuleService
from shared_db import get_db

router = APIRouter(prefix="/api/quality/rules", tags=["quality-rules"])


def get_quality_rule_service(db: Session = Depends(get_db)) -> QualityRuleService:
    return QualityRuleService(db_session=db)


@router.post("", response_model=QualityRuleResponse, status_code=201)
def create_rule(
    req: QualityRuleCreateRequest,
    service: QualityRuleService = Depends(get_quality_rule_service)
):
    result = service.create(
        rule_code=req.rule_code,
        rule_name=req.rule_name,
        rule_type=req.rule_type,
        severity=req.severity,
        description=req.description,
        config_json=req.config_json
    )
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to create quality rule")
    return result


@router.get("", response_model=list[QualityRuleResponse])
def list_rules(
    service: QualityRuleService = Depends(get_quality_rule_service)
):
    return service.list_all()


@router.get("/{rule_id}", response_model=QualityRuleResponse)
def get_rule(
    rule_id: int,
    service: QualityRuleService = Depends(get_quality_rule_service)
):
    result = service.get_by_id(rule_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Quality rule not found")
    return result
