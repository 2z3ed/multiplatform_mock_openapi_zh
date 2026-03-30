from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.quality_alert import QualityAlertResponse
from app.services.quality_alert_service import QualityAlertService
from shared_db import get_db

router = APIRouter(prefix="/api/quality/alerts", tags=["quality-alerts"])


def get_quality_alert_service(db: Session = Depends(get_db)) -> QualityAlertService:
    return QualityAlertService(db_session=db)


@router.get("", response_model=list[QualityAlertResponse])
def list_alerts(
    service: QualityAlertService = Depends(get_quality_alert_service)
):
    return service.list_all()


@router.get("/{alert_id}", response_model=QualityAlertResponse)
def get_alert(
    alert_id: int,
    service: QualityAlertService = Depends(get_quality_alert_service)
):
    result = service.get_by_id(alert_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Quality alert not found")
    return result
