from typing import Optional, Tuple

from sqlalchemy.orm import Session

from domain_models.models.risk_flag import RiskFlag
from app.repositories.risk_flag_repository import RiskFlagRepository
from app.services.audit_service import AuditService


class RiskFlagService:
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = RiskFlagRepository(db_session)
        self._audit_service = AuditService(db_session)

    def _to_dict(self, risk_flag: RiskFlag) -> dict:
        return {
            "id": risk_flag.id,
            "customer_id": risk_flag.customer_id,
            "conversation_id": risk_flag.conversation_id,
            "risk_type": risk_flag.risk_type,
            "risk_level": risk_flag.risk_level,
            "description": risk_flag.description,
            "extra_json": risk_flag.extra_json,
            "status": risk_flag.status,
            "created_at": risk_flag.created_at.isoformat() if risk_flag.created_at else None,
            "updated_at": risk_flag.updated_at.isoformat() if risk_flag.updated_at else None,
        }

    def create_risk_flag(
        self,
        customer_id: int,
        risk_type: str,
        conversation_id: Optional[int] = None,
        risk_level: str = "low",
        description: Optional[str] = None,
        extra_json: Optional[dict] = None,
    ) -> Optional[dict]:
        result = self._repo.create(
            customer_id=customer_id,
            risk_type=risk_type,
            conversation_id=conversation_id,
            risk_level=risk_level,
            description=description,
            extra_json=extra_json,
        )
        if result is None:
            return None

        self._audit_service.risk_flag_created(
            risk_flag_id=str(result.id),
            customer_id=str(result.customer_id),
            conversation_id=str(result.conversation_id) if result.conversation_id else None,
            risk_type=result.risk_type,
            risk_level=result.risk_level
        )

        return self._to_dict(result)

    def get_risk_flag_by_id(self, id: int) -> Optional[dict]:
        result = self._repo.get_by_id(id)
        if result is None:
            return None
        return self._to_dict(result)

    def list_risk_flags_by_customer_id(self, customer_id: int) -> list[dict]:
        results = self._repo.list_by_customer_id(customer_id)
        return [self._to_dict(r) for r in results]

    def resolve_risk_flag(self, id: int) -> Tuple[Optional[dict], Optional[str]]:
        existing = self._repo.get_by_id(id)
        if existing is None:
            return None, "not_found"
        if existing.status != "active":
            return None, "not_active"

        result = self._repo.update_status(id, "resolved")
        if result is None:
            return None, "update_failed"

        self._audit_service.risk_flag_resolved(
            risk_flag_id=str(result.id),
            customer_id=str(result.customer_id),
            conversation_id=str(result.conversation_id) if result.conversation_id else None,
            risk_type=result.risk_type,
            risk_level=result.risk_level
        )

        return self._to_dict(result), None

    def dismiss_risk_flag(self, id: int) -> Tuple[Optional[dict], Optional[str]]:
        existing = self._repo.get_by_id(id)
        if existing is None:
            return None, "not_found"
        if existing.status != "active":
            return None, "not_active"

        result = self._repo.update_status(id, "dismissed")
        if result is None:
            return None, "update_failed"

        self._audit_service.risk_flag_dismissed(
            risk_flag_id=str(result.id),
            customer_id=str(result.customer_id),
            conversation_id=str(result.conversation_id) if result.conversation_id else None,
            risk_type=result.risk_type,
            risk_level=result.risk_level
        )

        return self._to_dict(result), None
