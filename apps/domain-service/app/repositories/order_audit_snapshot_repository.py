from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.order_audit_snapshot import OrderAuditSnapshot, ALLOWED_AUDIT_STATUSES


class OrderAuditSnapshotRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        order_id: str,
        platform: str,
        audit_status: str,
        audit_reason: Optional[str] = None,
        source_json: Optional[dict] = None,
        snapshot_at: Optional[datetime] = None
    ) -> OrderAuditSnapshot:
        if snapshot_at is None:
            snapshot_at = datetime.utcnow()
        snapshot = OrderAuditSnapshot(
            order_id=order_id,
            platform=platform,
            audit_status=audit_status,
            audit_reason=audit_reason,
            source_json=source_json,
            snapshot_at=snapshot_at
        )
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def get_by_id(self, id: int) -> Optional[OrderAuditSnapshot]:
        return self.db.query(OrderAuditSnapshot).filter(OrderAuditSnapshot.id == id).first()

    def get_by_order_id(self, order_id: str) -> Optional[OrderAuditSnapshot]:
        return (
            self.db.query(OrderAuditSnapshot)
            .filter(OrderAuditSnapshot.order_id == order_id)
            .order_by(OrderAuditSnapshot.snapshot_at.desc())
            .first()
        )

    def list_all(self) -> list[OrderAuditSnapshot]:
        return (
            self.db.query(OrderAuditSnapshot)
            .order_by(OrderAuditSnapshot.snapshot_at.desc())
            .all()
        )

    def list_by_order_id(self, order_id: str) -> list[OrderAuditSnapshot]:
        return (
            self.db.query(OrderAuditSnapshot)
            .filter(OrderAuditSnapshot.order_id == order_id)
            .order_by(OrderAuditSnapshot.snapshot_at.desc())
            .all()
        )

    def delete(self, id: int) -> bool:
        snapshot = self.get_by_id(id)
        if snapshot is None:
            return False
        self.db.delete(snapshot)
        self.db.commit()
        return True
