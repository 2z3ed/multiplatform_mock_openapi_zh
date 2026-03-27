from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.customer_profile import CustomerProfile


class CustomerProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_customer_id(self, customer_id: int) -> Optional[CustomerProfile]:
        return self.db.query(CustomerProfile).filter(CustomerProfile.customer_id == customer_id).first()

    def create(
        self,
        customer_id: int,
        total_orders: int = 0,
        total_spent: Decimal = Decimal("0.00"),
        avg_order_value: Decimal = Decimal("0.00"),
        extra_json: Optional[dict] = None
    ) -> CustomerProfile:
        profile = CustomerProfile(
            customer_id=customer_id,
            total_orders=total_orders,
            total_spent=total_spent,
            avg_order_value=avg_order_value,
            extra_json=extra_json
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(
        self,
        customer_id: int,
        updates: dict
    ) -> Optional[CustomerProfile]:
        profile = self.get_by_customer_id(customer_id)
        if profile is None:
            return None

        for field_name, field_value in updates.items():
            if hasattr(profile, field_name):
                setattr(profile, field_name, field_value)

        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete(self, customer_id: int) -> bool:
        profile = self.get_by_customer_id(customer_id)
        if profile is None:
            return False
        self.db.delete(profile)
        self.db.commit()
        return True
