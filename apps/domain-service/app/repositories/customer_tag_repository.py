from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.customer_tag import CustomerTag


class CustomerTagRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, tag_id: int) -> Optional[CustomerTag]:
        return self.db.query(CustomerTag).filter(CustomerTag.id == tag_id).first()

    def list_by_customer_id(self, customer_id: int) -> list[CustomerTag]:
        return (
            self.db.query(CustomerTag)
            .filter(CustomerTag.customer_id == customer_id)
            .order_by(CustomerTag.created_at.desc())
            .all()
        )

    def create(
        self,
        customer_id: int,
        tag_type: str,
        tag_value: str,
        source: str = "manual",
        extra_json: Optional[dict] = None
    ) -> CustomerTag:
        tag = CustomerTag(
            customer_id=customer_id,
            tag_type=tag_type,
            tag_value=tag_value,
            source=source,
            extra_json=extra_json
        )
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def delete(self, tag_id: int) -> bool:
        tag = self.get_by_id(tag_id)
        if tag is None:
            return False
        self.db.delete(tag)
        self.db.commit()
        return True
