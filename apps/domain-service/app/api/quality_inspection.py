from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.quality_inspection_result import (
    QualityInspectRequest,
    QualityInspectionResultResponse
)
from app.services.quality_inspection_service import QualityInspectionService
from shared_db import get_db

router = APIRouter(prefix="/api/quality", tags=["quality-inspection"])


def get_quality_inspection_service(db: Session = Depends(get_db)) -> QualityInspectionService:
    return QualityInspectionService(db_session=db)


@router.post("/inspect", response_model=list[QualityInspectionResultResponse], status_code=200)
def inspect_conversation(
    req: QualityInspectRequest,
    service: QualityInspectionService = Depends(get_quality_inspection_service)
):
    return service.inspect_conversation(req.conversation_id)


@router.get("/results", response_model=list[QualityInspectionResultResponse])
def list_results(
    conversation_id: int | None = None,
    service: QualityInspectionService = Depends(get_quality_inspection_service)
):
    if conversation_id:
        return service.list_by_conversation(conversation_id)
    return service.list_all()


@router.get("/results/{result_id}", response_model=QualityInspectionResultResponse)
def get_result(
    result_id: int,
    service: QualityInspectionService = Depends(get_quality_inspection_service)
):
    result = service.get_by_id(result_id)
    if result is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Quality inspection result not found")
    return result
