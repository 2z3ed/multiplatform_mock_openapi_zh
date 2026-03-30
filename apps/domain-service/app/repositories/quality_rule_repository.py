from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.quality_rule import QualityRule, ALLOWED_RULE_TYPES, ALLOWED_SEVERITIES


class QualityRuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        rule_code: str,
        rule_name: str,
        rule_type: str,
        severity: str = "medium",
        description: Optional[str] = None,
        config_json: Optional[dict] = None
    ) -> QualityRule:
        rule = QualityRule(
            rule_code=rule_code,
            rule_name=rule_name,
            rule_type=rule_type,
            severity=severity,
            description=description,
            config_json=config_json
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule

    def get_by_id(self, id: int) -> Optional[QualityRule]:
        return self.db.query(QualityRule).filter(QualityRule.id == id).first()

    def get_by_rule_code(self, rule_code: str) -> Optional[QualityRule]:
        return self.db.query(QualityRule).filter(QualityRule.rule_code == rule_code).first()

    def list_all(self) -> list[QualityRule]:
        return (
            self.db.query(QualityRule)
            .order_by(QualityRule.created_at.desc())
            .all()
        )

    def list_by_rule_type(self, rule_type: str) -> list[QualityRule]:
        return (
            self.db.query(QualityRule)
            .filter(QualityRule.rule_type == rule_type)
            .order_by(QualityRule.created_at.desc())
            .all()
        )
