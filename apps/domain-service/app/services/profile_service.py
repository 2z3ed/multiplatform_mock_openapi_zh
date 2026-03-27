from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.customer_profile_repository import CustomerProfileRepository


class CustomerProfileService:
    """Customer profile service for V2"""

    ALLOWED_UPDATE_FIELDS = {"total_orders", "total_spent", "avg_order_value", "extra_json"}

    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = CustomerProfileRepository(db_session)

    def _to_dict(self, profile) -> dict:
        return {
            "id": profile.id,
            "customer_id": profile.customer_id,
            "total_orders": profile.total_orders,
            "total_spent": str(profile.total_spent),
            "avg_order_value": str(profile.avg_order_value),
            "extra_json": profile.extra_json,
            "created_at": profile.created_at.isoformat() if profile.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }

    def get_profile(self, customer_id: int) -> Optional[dict]:
        profile = self._repo.get_by_customer_id(customer_id)
        if profile is None:
            return None
        return self._to_dict(profile)

    def create_profile(
        self,
        customer_id: int,
        total_orders: int = 0,
        total_spent: Decimal = Decimal("0.00"),
        avg_order_value: Decimal = Decimal("0.00"),
        extra_json: Optional[dict] = None
    ) -> Optional[dict]:
        if total_orders < 0:
            return None
        if total_spent < 0:
            return None
        if avg_order_value < 0:
            return None

        existing = self._repo.get_by_customer_id(customer_id)
        if existing is not None:
            return None

        profile = self._repo.create(
            customer_id=customer_id,
            total_orders=total_orders,
            total_spent=total_spent,
            avg_order_value=avg_order_value,
            extra_json=extra_json
        )
        return self._to_dict(profile)

    def update_profile(self, customer_id: int, updates: dict) -> Optional[dict]:
        filtered_updates = {k: v for k, v in updates.items() if k in self.ALLOWED_UPDATE_FIELDS}
        if not filtered_updates:
            return None

        if "total_orders" in filtered_updates and filtered_updates["total_orders"] < 0:
            return None
        if "total_spent" in filtered_updates and filtered_updates["total_spent"] < 0:
            return None
        if "avg_order_value" in filtered_updates and filtered_updates["avg_order_value"] < 0:
            return None

        profile = self._repo.update(customer_id, filtered_updates)
        if profile is None:
            return None
        return self._to_dict(profile)

    def delete_profile(self, customer_id: int) -> bool:
        return self._repo.delete(customer_id)
