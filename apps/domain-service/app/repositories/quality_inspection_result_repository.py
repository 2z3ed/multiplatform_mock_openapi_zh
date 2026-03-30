from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.quality_inspection_result import QualityInspectionResult


class QualityInspectionResultRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        conversation_id: int,
        quality_rule_id: int,
        hit: bool,
        severity: str,
        evidence_json: Optional[dict] = None,
        inspected_at: Optional[str] = None
    ) -> QualityInspectionResult:
        result = QualityInspectionResult(
            conversation_id=conversation_id,
            quality_rule_id=quality_rule_id,
            hit=hit,
            severity=severity,
            evidence_json=evidence_json,
            inspected_at=inspected_at
        )
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def get_by_id(self, id: int) -> Optional[QualityInspectionResult]:
        return self.db.query(QualityInspectionResult).filter(QualityInspectionResult.id == id).first()

    def list_all(self) -> list[QualityInspectionResult]:
        return (
            self.db.query(QualityInspectionResult)
            .order_by(QualityInspectionResult.created_at.desc())
            .all()
        )

    def list_by_conversation(self, conversation_id: int) -> list[QualityInspectionResult]:
        return (
            self.db.query(QualityInspectionResult)
            .filter(QualityInspectionResult.conversation_id == conversation_id)
            .order_by(QualityInspectionResult.created_at.desc())
            .all()
        )

    def list_by_rule(self, quality_rule_id: int) -> list[QualityInspectionResult]:
        return (
            self.db.query(QualityInspectionResult)
            .filter(QualityInspectionResult.quality_rule_id == quality_rule_id)
            .order_by(QualityInspectionResult.created_at.desc())
            .all()
        )

    def list_hit_only(self) -> list[QualityInspectionResult]:
        return (
            self.db.query(QualityInspectionResult)
            .filter(QualityInspectionResult.hit == True)
            .order_by(QualityInspectionResult.created_at.desc())
            .all()
        )

    def list_high_severity_hit(self) -> list[QualityInspectionResult]:
        return (
            self.db.query(QualityInspectionResult)
            .filter(QualityInspectionResult.hit == True)
            .filter(QualityInspectionResult.severity == "high")
            .order_by(QualityInspectionResult.created_at.desc())
            .all()
        )
