from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.erp_inventory_snapshot import ERPInventorySnapshot, ALLOWED_INVENTORY_STATUSES


class ERPInventorySnapshotRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        sku_code: str,
        warehouse_code: str,
        available_qty: int,
        reserved_qty: int = 0,
        status: str = "normal",
        source_json: Optional[dict] = None,
        snapshot_at: Optional[datetime] = None
    ) -> ERPInventorySnapshot:
        if snapshot_at is None:
            snapshot_at = datetime.utcnow()
        snapshot = ERPInventorySnapshot(
            sku_code=sku_code,
            warehouse_code=warehouse_code,
            available_qty=available_qty,
            reserved_qty=reserved_qty,
            status=status,
            source_json=source_json,
            snapshot_at=snapshot_at
        )
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def get_by_id(self, id: int) -> Optional[ERPInventorySnapshot]:
        return self.db.query(ERPInventorySnapshot).filter(ERPInventorySnapshot.id == id).first()

    def get_by_sku_code(self, sku_code: str) -> Optional[ERPInventorySnapshot]:
        return (
            self.db.query(ERPInventorySnapshot)
            .filter(ERPInventorySnapshot.sku_code == sku_code)
            .order_by(ERPInventorySnapshot.snapshot_at.desc())
            .first()
        )

    def list_all(self) -> list[ERPInventorySnapshot]:
        return (
            self.db.query(ERPInventorySnapshot)
            .order_by(ERPInventorySnapshot.snapshot_at.desc())
            .all()
        )

    def list_by_sku_code(self, sku_code: str) -> list[ERPInventorySnapshot]:
        return (
            self.db.query(ERPInventorySnapshot)
            .filter(ERPInventorySnapshot.sku_code == sku_code)
            .order_by(ERPInventorySnapshot.snapshot_at.desc())
            .all()
        )

    def delete(self, id: int) -> bool:
        snapshot = self.get_by_id(id)
        if snapshot is None:
            return False
        self.db.delete(snapshot)
        self.db.commit()
        return True

    def cleanup_old_snapshots(
        self,
        retention_days: int = 7,
        dry_run: bool = True,
    ) -> dict:
        """Cleanup old snapshots based on retention days.
        
        Args:
            retention_days: Number of days to retain snapshots.
            dry_run: If True, only preview without deleting.
            
        Returns:
            dict with total_count, to_delete_count, protected_count, deleted_count
        """
        from datetime import timedelta
        from sqlalchemy import and_
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        total_count = self.db.query(ERPInventorySnapshot).count()
        
        latest_snapshot = (
            self.db.query(ERPInventorySnapshot)
            .order_by(ERPInventorySnapshot.snapshot_at.desc())
            .first()
        )
        
        protected_ids = []
        if latest_snapshot:
            protected_ids.append(latest_snapshot.id)
        
        to_delete_query = self.db.query(ERPInventorySnapshot).filter(
            and_(
                ERPInventorySnapshot.snapshot_at < cutoff_date,
                ERPInventorySnapshot.id.notin_(protected_ids) if protected_ids else True,
            )
        )
        
        to_delete_count = to_delete_query.count()
        protected_count = len(protected_ids)
        deleted_count = 0
        
        if not dry_run and to_delete_count > 0:
            for snapshot in to_delete_query.all():
                self.db.delete(snapshot)
            self.db.commit()
            deleted_count = to_delete_count
        
        return {
            "total_count": total_count,
            "to_delete_count": to_delete_count,
            "protected_count": protected_count,
            "deleted_count": deleted_count,
        }
