from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.order_exception_snapshot import OrderExceptionSnapshot, ALLOWED_EXCEPTION_TYPES, ALLOWED_EXCEPTION_STATUSES


class OrderExceptionSnapshotRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        order_id: str,
        platform: str,
        exception_type: str,
        exception_status: str,
        detail_json: Optional[dict] = None,
        snapshot_at: Optional[datetime] = None
    ) -> OrderExceptionSnapshot:
        if snapshot_at is None:
            snapshot_at = datetime.utcnow()
        snapshot = OrderExceptionSnapshot(
            order_id=order_id,
            platform=platform,
            exception_type=exception_type,
            exception_status=exception_status,
            detail_json=detail_json,
            snapshot_at=snapshot_at
        )
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def get_by_id(self, id: int) -> Optional[OrderExceptionSnapshot]:
        return self.db.query(OrderExceptionSnapshot).filter(OrderExceptionSnapshot.id == id).first()

    def get_by_order_id(self, order_id: str) -> Optional[OrderExceptionSnapshot]:
        return (
            self.db.query(OrderExceptionSnapshot)
            .filter(OrderExceptionSnapshot.order_id == order_id)
            .order_by(OrderExceptionSnapshot.snapshot_at.desc())
            .first()
        )

    def list_all(self) -> list[OrderExceptionSnapshot]:
        return (
            self.db.query(OrderExceptionSnapshot)
            .order_by(OrderExceptionSnapshot.snapshot_at.desc())
            .all()
        )

    def list_by_order_id(self, order_id: str) -> list[OrderExceptionSnapshot]:
        return (
            self.db.query(OrderExceptionSnapshot)
            .filter(OrderExceptionSnapshot.order_id == order_id)
            .order_by(OrderExceptionSnapshot.snapshot_at.desc())
            .all()
        )

    def list_by_exception_type(self, exception_type: str) -> list[OrderExceptionSnapshot]:
        return (
            self.db.query(OrderExceptionSnapshot)
            .filter(OrderExceptionSnapshot.exception_type == exception_type)
            .order_by(OrderExceptionSnapshot.snapshot_at.desc())
            .all()
        )

    def delete(self, id: int) -> bool:
        snapshot = self.get_by_id(id)
        if snapshot is None:
            return False
        self.db.delete(snapshot)
        self.db.commit()
        return True
