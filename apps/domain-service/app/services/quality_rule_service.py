from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.quality_rule_repository import QualityRuleRepository
from app.services.audit_service import AuditService
from domain_models.models.quality_rule import ALLOWED_RULE_TYPES, ALLOWED_SEVERITIES


class QualityRuleService:
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = QualityRuleRepository(db_session)
        self._audit_service = AuditService(db_session=db_session)

    def _to_dict(self, rule) -> dict:
        return {
            "id": rule.id,
            "rule_code": rule.rule_code,
            "rule_name": rule.rule_name,
            "rule_type": rule.rule_type,
            "severity": rule.severity,
            "description": rule.description,
            "config_json": rule.config_json,
            "created_at": rule.created_at.isoformat() if rule.created_at else None,
            "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
        }

    def get_by_id(self, id: int) -> Optional[dict]:
        rule = self._repo.get_by_id(id)
        if rule is None:
            return None
        return self._to_dict(rule)

    def get_by_rule_code(self, rule_code: str) -> Optional[dict]:
        rule = self._repo.get_by_rule_code(rule_code)
        if rule is None:
            return None
        return self._to_dict(rule)

    def list_all(self) -> list[dict]:
        rules = self._repo.list_all()
        return [self._to_dict(r) for r in rules]

    def list_by_rule_type(self, rule_type: str) -> list[dict]:
        if rule_type not in ALLOWED_RULE_TYPES:
            return []
        rules = self._repo.list_by_rule_type(rule_type)
        return [self._to_dict(r) for r in rules]

    def create(
        self,
        rule_code: str,
        rule_name: str,
        rule_type: str,
        severity: str = "medium",
        description: Optional[str] = None,
        config_json: Optional[dict] = None
    ) -> Optional[dict]:
        if rule_type not in ALLOWED_RULE_TYPES:
            return None
        if severity not in ALLOWED_SEVERITIES:
            return None

        existing = self._repo.get_by_rule_code(rule_code)
        if existing is not None:
            return None

        rule = self._repo.create(
            rule_code=rule_code,
            rule_name=rule_name,
            rule_type=rule_type,
            severity=severity,
            description=description,
            config_json=config_json
        )

        self._audit_service.log_event(
            action="quality_rule_created",
            target_type="quality_rule",
            target_id=str(rule.id),
            detail=f"Created quality rule: {rule_name}",
            detail_json={
                "rule_id": rule.id,
                "rule_code": rule_code,
                "rule_name": rule_name,
                "rule_type": rule_type,
                "severity": severity
            }
        )

        return self._to_dict(rule)
