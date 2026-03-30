from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.blacklist_customer import BlacklistCustomer, ALLOWED_SOURCES


class BlacklistCustomerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        customer_id: int,
        reason: Optional[str] = None,
        source: str = "manual"
    ) -> BlacklistCustomer:
        blacklist = BlacklistCustomer(
            customer_id=customer_id,
            reason=reason,
            source=source
        )
        self.db.add(blacklist)
        self.db.commit()
        self.db.refresh(blacklist)
        return blacklist

    def get_by_id(self, id: int) -> Optional[BlacklistCustomer]:
        return self.db.query(BlacklistCustomer).filter(BlacklistCustomer.id == id).first()

    def get_by_customer_id(self, customer_id: int) -> Optional[BlacklistCustomer]:
        return self.db.query(BlacklistCustomer).filter(BlacklistCustomer.customer_id == customer_id).first()

    def list_all(self) -> list[BlacklistCustomer]:
        return (
            self.db.query(BlacklistCustomer)
            .order_by(BlacklistCustomer.created_at.desc())
            .all()
        )

    def list_by_source(self, source: str) -> list[BlacklistCustomer]:
        return (
            self.db.query(BlacklistCustomer)
            .filter(BlacklistCustomer.source == source)
            .order_by(BlacklistCustomer.created_at.desc())
            .all()
        )

    def delete_by_customer_id(self, customer_id: int) -> bool:
        blacklist = self.get_by_customer_id(customer_id)
        if blacklist is None:
            return False
        self.db.delete(blacklist)
        self.db.commit()
        return True

    def exists(self, customer_id: int) -> bool:
        return self.get_by_customer_id(customer_id) is not None
