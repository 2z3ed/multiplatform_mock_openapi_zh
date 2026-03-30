from datetime import date
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.management import (
    VOCTopicCreateRequest,
    VOCTopicResponse,
    TrainingCaseCreateRequest,
    TrainingCaseResponse,
    TrainingTaskCreateRequest,
    TrainingTaskResponse,
    DashboardSnapshotCreateRequest,
    DashboardSnapshotResponse,
)
from app.services.management_service import ManagementService
from shared_db import get_db

router = APIRouter(prefix="/api/management", tags=["management"])


def get_management_service(db: Session = Depends(get_db)) -> ManagementService:
    return ManagementService(db_session=db)


@router.post("/voc-topics", response_model=VOCTopicResponse, status_code=201)
def create_voc_topic(
    req: VOCTopicCreateRequest,
    service: ManagementService = Depends(get_management_service)
):
    try:
        result = service.create_voc_topic(
            topic_name=req.topic_name,
            topic_type=req.topic_type,
            source=req.source,
            occurrence_count=req.occurrence_count,
            summary=req.summary,
            extra_json=req.extra_json
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/voc-topics", response_model=list[VOCTopicResponse])
def list_voc_topics(
    topic_type: str | None = Query(None, description="Filter by topic type"),
    service: ManagementService = Depends(get_management_service)
):
    return service.list_voc_topics(topic_type=topic_type)


@router.post("/training-cases", response_model=TrainingCaseResponse, status_code=201)
def create_training_case(
    req: TrainingCaseCreateRequest,
    service: ManagementService = Depends(get_management_service)
):
    try:
        result = service.create_training_case(
            case_title=req.case_title,
            case_type=req.case_type,
            conversation_id=req.conversation_id,
            customer_id=req.customer_id,
            case_summary=req.case_summary,
            source_json=req.source_json
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/training-cases", response_model=list[TrainingCaseResponse])
def list_training_cases(
    case_type: str | None = Query(None, description="Filter by case type"),
    service: ManagementService = Depends(get_management_service)
):
    return service.list_training_cases(case_type=case_type)


@router.post("/training-tasks", response_model=TrainingTaskResponse, status_code=201)
def create_training_task(
    req: TrainingTaskCreateRequest,
    service: ManagementService = Depends(get_management_service)
):
    try:
        result = service.create_training_task(
            task_name=req.task_name,
            task_type=req.task_type,
            status=req.status,
            related_case_id=req.related_case_id,
            detail_json=req.detail_json
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/training-tasks", response_model=list[TrainingTaskResponse])
def list_training_tasks(
    status: str | None = Query(None, description="Filter by status"),
    service: ManagementService = Depends(get_management_service)
):
    return service.list_training_tasks(status=status)


@router.post("/dashboard-snapshots", response_model=DashboardSnapshotResponse, status_code=201)
def create_dashboard_snapshot(
    req: DashboardSnapshotCreateRequest,
    service: ManagementService = Depends(get_management_service)
):
    try:
        result = service.create_dashboard_snapshot(
            snapshot_date=req.snapshot_date,
            metric_type=req.metric_type,
            metric_value=req.metric_value,
            detail_json=req.detail_json
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dashboard-snapshots", response_model=list[DashboardSnapshotResponse])
def list_dashboard_snapshots(
    metric_type: str | None = Query(None, description="Filter by metric type"),
    snapshot_date: date | None = Query(None, description="Filter by snapshot date"),
    service: ManagementService = Depends(get_management_service)
):
    return service.list_dashboard_snapshots(metric_type=metric_type, snapshot_date=snapshot_date)
