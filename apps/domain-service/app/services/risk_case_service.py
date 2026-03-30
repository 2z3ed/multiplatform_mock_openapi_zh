from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.risk_case_repository import RiskCaseRepository
from app.services.audit_service import AuditService
from domain_models.models.risk_case import ALLOWED_RISK_TYPES, ALLOWED_SEVERITIES, ALLOWED_STATUSES


class InvalidStateTransitionError(Exception):
    pass


class RiskCaseService:
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = RiskCaseRepository(db_session)
        self._audit_service = AuditService(db_session=db_session)

    def _to_dict(self, risk_case) -> dict:
        return {
            "id": risk_case.id,
            "conversation_id": risk_case.conversation_id,
            "customer_id": risk_case.customer_id,
            "risk_type": risk_case.risk_type,
            "severity": risk_case.severity,
            "status": risk_case.status,
            "evidence_json": risk_case.evidence_json,
            "created_at": risk_case.created_at.isoformat() if risk_case.created_at else None,
            "updated_at": risk_case.updated_at.isoformat() if risk_case.updated_at else None,
        }

    def get_by_id(self, id: int) -> Optional[dict]:
        risk_case = self._repo.get_by_id(id)
        if risk_case is None:
            return None
        return self._to_dict(risk_case)

    def list_all(self) -> list[dict]:
        cases = self._repo.list_all()
        return [self._to_dict(c) for c in cases]

    def list_by_customer(self, customer_id: int) -> list[dict]:
        cases = self._repo.list_by_customer(customer_id)
        return [self._to_dict(c) for c in cases]

    def create(
        self,
        conversation_id: int,
        customer_id: int,
        risk_type: str,
        severity: str = "medium",
        evidence_json: Optional[dict] = None
    ) -> Optional[dict]:
        if risk_type not in ALLOWED_RISK_TYPES:
            return None
        if severity not in ALLOWED_SEVERITIES:
            return None

        risk_case = self._repo.create(
            conversation_id=conversation_id,
            customer_id=customer_id,
            risk_type=risk_type,
            severity=severity,
            evidence_json=evidence_json
        )

        self._audit_service.log_event(
            action="risk_case_created",
            target_type="risk_case",
            target_id=str(risk_case.id),
            detail=f"Created risk case: {risk_type}",
            detail_json={
                "risk_case_id": risk_case.id,
                "conversation_id": conversation_id,
                "customer_id": customer_id,
                "risk_type": risk_type,
                "severity": severity
            }
        )

        return self._to_dict(risk_case)

    def resolve(self, id: int) -> Optional[dict]:
        risk_case = self._repo.get_by_id(id)
        if risk_case is None:
            return None
        if risk_case.status != "open":
            raise InvalidStateTransitionError(f"Cannot resolve risk case in status '{risk_case.status}'")

        self._repo.update_status(id, "resolved")

        self._audit_service.log_event(
            action="risk_case_resolved",
            target_type="risk_case",
            target_id=str(id),
            detail=f"Resolved risk case {id}",
            detail_json={"risk_case_id": id, "new_status": "resolved"}
        )

        return self.get_by_id(id)

    def dismiss(self, id: int) -> Optional[dict]:
        risk_case = self._repo.get_by_id(id)
        if risk_case is None:
            return None
        if risk_case.status != "open":
            raise InvalidStateTransitionError(f"Cannot dismiss risk case in status '{risk_case.status}'")

        self._repo.update_status(id, "dismissed")

        self._audit_service.log_event(
            action="risk_case_dismissed",
            target_type="risk_case",
            target_id=str(id),
            detail=f"Dismissed risk case {id}",
            detail_json={"risk_case_id": id, "new_status": "dismissed"}
        )

        return self.get_by_id(id)

    def escalate(self, id: int) -> Optional[dict]:
        risk_case = self._repo.get_by_id(id)
        if risk_case is None:
            return None
        if risk_case.status != "open":
            raise InvalidStateTransitionError(f"Cannot escalate risk case in status '{risk_case.status}'")

        self._repo.update_status(id, "escalated")

        self._audit_service.log_event(
            action="risk_case_escalated",
            target_type="risk_case",
            target_id=str(id),
            detail=f"Escalated risk case {id}",
            detail_json={"risk_case_id": id, "new_status": "escalated"}
        )

        return self.get_by_id(id)
