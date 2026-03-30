from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.management_dashboard_snapshot import ManagementDashboardSnapshot, ALLOWED_METRIC_TYPES


class ManagementDashboardSnapshotRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        snapshot_date: date,
        metric_type: str,
        metric_value: float,
        detail_json: Optional[dict] = None
    ) -> ManagementDashboardSnapshot:
        snapshot = ManagementDashboardSnapshot(
            snapshot_date=snapshot_date,
            metric_type=metric_type,
            metric_value=metric_value,
            detail_json=detail_json
        )
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)
        return snapshot

    def get_by_id(self, id: int) -> Optional[ManagementDashboardSnapshot]:
        return self.db.query(ManagementDashboardSnapshot).filter(ManagementDashboardSnapshot.id == id).first()

    def list_all(self) -> list[ManagementDashboardSnapshot]:
        return self.db.query(ManagementDashboardSnapshot).order_by(ManagementDashboardSnapshot.snapshot_date.desc()).all()

    def list_by_metric_type(self, metric_type: str) -> list[ManagementDashboardSnapshot]:
        return (
            self.db.query(ManagementDashboardSnapshot)
            .filter(ManagementDashboardSnapshot.metric_type == metric_type)
            .order_by(ManagementDashboardSnapshot.snapshot_date.desc())
            .all()
        )

    def list_by_date(self, snapshot_date: date) -> list[ManagementDashboardSnapshot]:
        return (
            self.db.query(ManagementDashboardSnapshot)
            .filter(ManagementDashboardSnapshot.snapshot_date == snapshot_date)
            .order_by(ManagementDashboardSnapshot.metric_type)
            .all()
        )

    def delete(self, id: int) -> bool:
        snapshot = self.get_by_id(id)
        if snapshot is None:
            return False
        self.db.delete(snapshot)
        self.db.commit()
        return True
