from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.followup import (
    CreateFollowUpTaskRequest,
    UpdateFollowUpTaskRequest,
    ExecuteFollowUpTaskRequest,
    CloseFollowUpTaskRequest,
    FollowUpTaskResponse,
    FollowUpTaskListResponse
)
from app.services.followup_service import FollowUpTaskService
from shared_db import get_db

router = APIRouter(prefix="/api/follow-up", tags=["follow-up"])


def get_followup_service(db: Session = Depends(get_db)) -> FollowUpTaskService:
    return FollowUpTaskService(db_session=db)


@router.get("/tasks", response_model=FollowUpTaskListResponse)
def list_tasks(
    customer_id: Optional[int] = Query(None),
    conversation_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: FollowUpTaskService = Depends(get_followup_service)
):
    items, total = service.list_tasks(
        customer_id=customer_id,
        conversation_id=conversation_id,
        status=status,
        task_type=task_type,
        priority=priority,
        page=page,
        size=size
    )
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size
    }


@router.post("/tasks", response_model=FollowUpTaskResponse, status_code=201)
def create_task(
    req: CreateFollowUpTaskRequest,
    service: FollowUpTaskService = Depends(get_followup_service)
):
    result = service.create_task(
        customer_id=req.customer_id,
        task_type=req.task_type,
        title=req.title,
        trigger_source=req.trigger_source,
        conversation_id=req.conversation_id,
        order_id=req.order_id,
        description=req.description,
        suggested_copy=req.suggested_copy,
        priority=req.priority,
        due_date=req.due_date,
        extra_json=req.extra_json
    )
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid task parameters")
    return result


@router.get("/tasks/{task_id}", response_model=FollowUpTaskResponse)
def get_task(
    task_id: int,
    service: FollowUpTaskService = Depends(get_followup_service)
):
    result = service.get_task(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@router.patch("/tasks/{task_id}", response_model=FollowUpTaskResponse)
def update_task(
    task_id: int,
    req: UpdateFollowUpTaskRequest,
    service: FollowUpTaskService = Depends(get_followup_service)
):
    updates = req.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    existing = service.get_task(task_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    result = service.update_task(task_id, updates)
    if result is None:
        raise HTTPException(status_code=400, detail="Invalid priority value")
    return result


@router.post("/tasks/{task_id}/execute", response_model=FollowUpTaskResponse)
def execute_task(
    task_id: int,
    req: ExecuteFollowUpTaskRequest,
    service: FollowUpTaskService = Depends(get_followup_service)
):
    result = service.execute_task(task_id, req.completed_by)
    if result is None:
        existing = service.get_task(task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(status_code=400, detail="Task is not in pending status")
    return result


@router.post("/tasks/{task_id}/close", response_model=FollowUpTaskResponse)
def close_task(
    task_id: int,
    req: CloseFollowUpTaskRequest,
    service: FollowUpTaskService = Depends(get_followup_service)
):
    result = service.close_task(task_id, req.completed_by)
    if result is None:
        existing = service.get_task(task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail="Task not found")
        raise HTTPException(status_code=400, detail="Task is not in pending status")
    return result
