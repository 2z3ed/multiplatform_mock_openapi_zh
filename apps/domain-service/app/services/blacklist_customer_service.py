from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.blacklist_customer_repository import BlacklistCustomerRepository
from app.services.audit_service import AuditService
from domain_models.models.blacklist_customer import ALLOWED_SOURCES


class BlacklistCustomerService:
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = BlacklistCustomerRepository(db_session)
        self._audit_service = AuditService(db_session=db_session)

    def _to_dict(self, blacklist) -> dict:
        return {
            "id": blacklist.id,
            "customer_id": blacklist.customer_id,
            "reason": blacklist.reason,
            "source": blacklist.source,
            "created_at": blacklist.created_at.isoformat() if blacklist.created_at else None,
            "updated_at": blacklist.updated_at.isoformat() if blacklist.updated_at else None,
        }

    def get_by_id(self, id: int) -> Optional[dict]:
        blacklist = self._repo.get_by_id(id)
        if blacklist is None:
            return None
        return self._to_dict(blacklist)

    def get_by_customer_id(self, customer_id: int) -> Optional[dict]:
        blacklist = self._repo.get_by_customer_id(customer_id)
        if blacklist is None:
            return None
        return self._to_dict(blacklist)

    def list_all(self) -> list[dict]:
        blacklists = self._repo.list_all()
        return [self._to_dict(b) for b in blacklists]

    def create(
        self,
        customer_id: int,
        reason: Optional[str] = None,
        source: str = "manual"
    ) -> Optional[dict]:
        if source not in ALLOWED_SOURCES:
            return None

        if self._repo.exists(customer_id):
            return None

        blacklist = self._repo.create(
            customer_id=customer_id,
            reason=reason,
            source=source
        )

        self._audit_service.log_event(
            action="blacklist_customer_created",
            target_type="blacklist_customer",
            target_id=str(blacklist.id),
            detail=f"Added customer {customer_id} to blacklist",
            detail_json={
                "blacklist_id": blacklist.id,
                "customer_id": customer_id,
                "source": source
            }
        )

        return self._to_dict(blacklist)

    def delete(self, customer_id: int) -> bool:
        blacklist = self._repo.get_by_customer_id(customer_id)
        if blacklist is None:
            return False

        blacklist_id = blacklist.id

        success = self._repo.delete_by_customer_id(customer_id)
        if success:
            self._audit_service.log_event(
                action="blacklist_customer_removed",
                target_type="blacklist_customer",
                target_id=str(blacklist_id),
                detail=f"Removed customer {customer_id} from blacklist",
                detail_json={
                    "blacklist_id": blacklist_id,
                    "customer_id": customer_id
                }
            )

        return success
