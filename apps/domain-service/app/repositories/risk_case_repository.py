from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.risk_case import RiskCase, ALLOWED_RISK_TYPES, ALLOWED_SEVERITIES, ALLOWED_STATUSES


class RiskCaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        conversation_id: int,
        customer_id: int,
        risk_type: str,
        severity: str = "medium",
        evidence_json: Optional[dict] = None
    ) -> RiskCase:
        risk_case = RiskCase(
            conversation_id=conversation_id,
            customer_id=customer_id,
            risk_type=risk_type,
            severity=severity,
            status="open",
            evidence_json=evidence_json
        )
        self.db.add(risk_case)
        self.db.commit()
        self.db.refresh(risk_case)
        return risk_case

    def get_by_id(self, id: int) -> Optional[RiskCase]:
        return self.db.query(RiskCase).filter(RiskCase.id == id).first()

    def list_all(self) -> list[RiskCase]:
        return (
            self.db.query(RiskCase)
            .order_by(RiskCase.created_at.desc())
            .all()
        )

    def list_by_customer(self, customer_id: int) -> list[RiskCase]:
        return (
            self.db.query(RiskCase)
            .filter(RiskCase.customer_id == customer_id)
            .order_by(RiskCase.created_at.desc())
            .all()
        )

    def list_by_status(self, status: str) -> list[RiskCase]:
        return (
            self.db.query(RiskCase)
            .filter(RiskCase.status == status)
            .order_by(RiskCase.created_at.desc())
            .all()
        )

    def list_by_severity(self, severity: str) -> list[RiskCase]:
        return (
            self.db.query(RiskCase)
            .filter(RiskCase.severity == severity)
            .order_by(RiskCase.created_at.desc())
            .all()
        )

    def update_status(self, id: int, new_status: str) -> Optional[RiskCase]:
        risk_case = self.get_by_id(id)
        if risk_case is None:
            return None
        risk_case.status = new_status
        self.db.commit()
        self.db.refresh(risk_case)
        return risk_case

    def delete(self, id: int) -> bool:
        risk_case = self.get_by_id(id)
        if risk_case is None:
            return False
        self.db.delete(risk_case)
        self.db.commit()
        return True
