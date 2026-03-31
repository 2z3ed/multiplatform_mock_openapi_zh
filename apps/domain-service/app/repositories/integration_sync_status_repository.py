from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from domain_models.models.integration_sync_status import (
    IntegrationSyncStatus,
    ALLOWED_SYNC_STATUSES,
    ALLOWED_TRIGGER_TYPES,
    ALLOWED_PROVIDER_MODES,
)


class IntegrationSyncStatusRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        trigger_type: str = "manual",
        provider_mode: str = "mock",
        started_at: Optional[datetime] = None,
    ) -> IntegrationSyncStatus:
        if trigger_type not in ALLOWED_TRIGGER_TYPES:
            raise ValueError(f"Invalid trigger_type: {trigger_type}")
        if provider_mode not in ALLOWED_PROVIDER_MODES:
            raise ValueError(f"Invalid provider_mode: {provider_mode}")
        
        status = IntegrationSyncStatus(
            trigger_type=trigger_type,
            provider_mode=provider_mode,
            started_at=started_at or datetime.utcnow(),
            status="success",
        )
        self.db.add(status)
        self.db.commit()
        self.db.refresh(status)
        return status

    def update(
        self,
        sync_status: IntegrationSyncStatus,
        finished_at: Optional[datetime] = None,
        status: str = "success",
        error_summary: Optional[str] = None,
        inventory_count: int = 0,
        audit_count: int = 0,
        exception_count: int = 0,
    ) -> IntegrationSyncStatus:
        if status not in ALLOWED_SYNC_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        
        sync_status.finished_at = finished_at or datetime.utcnow()
        sync_status.status = status
        sync_status.error_summary = error_summary
        sync_status.inventory_count = inventory_count
        sync_status.audit_count = audit_count
        sync_status.exception_count = exception_count
        
        self.db.commit()
        self.db.refresh(sync_status)
        return sync_status

    def get_latest(self) -> Optional[IntegrationSyncStatus]:
        return (
            self.db.query(IntegrationSyncStatus)
            .order_by(IntegrationSyncStatus.started_at.desc())
            .first()
        )

    def get_by_id(self, sync_id: int) -> Optional[IntegrationSyncStatus]:
        return self.db.query(IntegrationSyncStatus).filter(IntegrationSyncStatus.id == sync_id).first()
