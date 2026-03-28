from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.customer_tag_repository import CustomerTagRepository
from app.services.audit_service import AuditService


class CustomerTagService:
    """Customer tag service for V2"""

    VALID_TAG_TYPES = {"behavior", "preference", "segment", "custom"}
    VALID_SOURCES = {"manual"}

    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = CustomerTagRepository(db_session)
        self._audit_service = AuditService(db_session=db_session)

    def _to_dict(self, tag) -> dict:
        return {
            "id": tag.id,
            "customer_id": tag.customer_id,
            "tag_type": tag.tag_type,
            "tag_value": tag.tag_value,
            "source": tag.source,
            "extra_json": tag.extra_json,
            "created_at": tag.created_at.isoformat() if tag.created_at else None,
            "updated_at": tag.updated_at.isoformat() if tag.updated_at else None,
        }

    def get_tag(self, tag_id: int) -> Optional[dict]:
        tag = self._repo.get_by_id(tag_id)
        if tag is None:
            return None
        return self._to_dict(tag)

    def list_tags(self, customer_id: int) -> list[dict]:
        tags = self._repo.list_by_customer_id(customer_id)
        return [self._to_dict(t) for t in tags]

    def create_tag(
        self,
        customer_id: int,
        tag_type: str,
        tag_value: str,
        source: str = "manual",
        extra_json: Optional[dict] = None
    ) -> Optional[dict]:
        if tag_type not in self.VALID_TAG_TYPES:
            return None

        if source not in self.VALID_SOURCES:
            return None

        existing_tags = self._repo.list_by_customer_id(customer_id)
        for tag in existing_tags:
            if tag.tag_type == tag_type and tag.tag_value == tag_value:
                return None

        tag = self._repo.create(
            customer_id=customer_id,
            tag_type=tag_type,
            tag_value=tag_value,
            source=source,
            extra_json=extra_json
        )
        
        self._audit_service.customer_tag_created(
            tag_id=str(tag.id),
            customer_id=str(customer_id),
            tag_type=tag_type,
            tag_value=tag_value
        )
        
        return self._to_dict(tag)

    def delete_tag(self, tag_id: int) -> bool:
        tag = self._repo.get_by_id(tag_id)
        if tag is None:
            return False
        
        customer_id = tag.customer_id
        tag_type = tag.tag_type
        tag_value = tag.tag_value
        
        result = self._repo.delete(tag_id)
        if result:
            self._audit_service.customer_tag_deleted(
                tag_id=str(tag_id),
                customer_id=str(customer_id),
                tag_type=tag_type,
                tag_value=tag_value
            )
        
        return result
