from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.quality_alert import QualityAlert


class QualityAlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        quality_inspection_result_id: int,
        alert_level: str = "high"
    ) -> QualityAlert:
        alert = QualityAlert(
            quality_inspection_result_id=quality_inspection_result_id,
            alert_level=alert_level
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_by_id(self, id: int) -> Optional[QualityAlert]:
        return self.db.query(QualityAlert).filter(QualityAlert.id == id).first()

    def get_by_result_id(self, quality_inspection_result_id: int) -> Optional[QualityAlert]:
        return (
            self.db.query(QualityAlert)
            .filter(QualityAlert.quality_inspection_result_id == quality_inspection_result_id)
            .first()
        )

    def list_all(self) -> list[QualityAlert]:
        return (
            self.db.query(QualityAlert)
            .order_by(QualityAlert.created_at.desc())
            .all()
        )

    def exists_for_result(self, quality_inspection_result_id: int) -> bool:
        return (
            self.db.query(QualityAlert)
            .filter(QualityAlert.quality_inspection_result_id == quality_inspection_result_id)
            .first()
            is not None
        )
