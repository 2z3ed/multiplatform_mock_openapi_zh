from typing import Optional
from sqlalchemy.orm import Session

from app.repositories.quality_alert_repository import QualityAlertRepository
from app.services.audit_service import AuditService


class QualityAlertService:
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = QualityAlertRepository(db_session)
        self._audit_service = AuditService(db_session=db_session)

    def _to_dict(self, alert) -> dict:
        return {
            "id": alert.id,
            "quality_inspection_result_id": alert.quality_inspection_result_id,
            "alert_level": alert.alert_level,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
        }

    def get_by_id(self, id: int) -> Optional[dict]:
        alert = self._repo.get_by_id(id)
        if alert is None:
            return None
        return self._to_dict(alert)

    def list_all(self) -> list[dict]:
        alerts = self._repo.list_all()
        return [self._to_dict(a) for a in alerts]
