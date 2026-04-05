from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session

from app.schemas.followup import (
    CreateFollowUpTaskRequest,
    UpdateFollowUpTaskRequest,
    ExecuteFollowUpTaskRequest,
    CloseFollowUpTaskRequest,
    FollowUpTaskResponse,
    FollowUpTaskListResponse,
    AutoEvaluateFollowupRequest,
    AutoEvaluateFollowupResponse,
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


@router.post("/auto-evaluate", response_model=AutoEvaluateFollowupResponse)
def auto_evaluate_followup(
    req: AutoEvaluateFollowupRequest,
    db: Session = Depends(get_db),
    service: FollowUpTaskService = Depends(get_followup_service),
):
    from app.services.context_aggregation_service import aggregate_conversation_context
    from app.services.followup_rule_service import evaluate_conversation_for_followup

    try:
        conv_id = int(req.conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid conversation_id")

    context = aggregate_conversation_context(db, conv_id)

    task_payloads = evaluate_conversation_for_followup(
        conversation_context=context,
        conversation_id=conv_id,
        customer_id=req.customer_id,
        order_timeout_hours=req.order_timeout_hours or 24,
        after_sale_timeout_hours=req.after_sale_timeout_hours or 48,
    )

    created = []
    skipped = 0
    for payload in task_payloads:
        existing_tasks, _ = service.list_tasks(
            conversation_id=conv_id,
            task_type=payload["task_type"],
            status="pending",
            page=1,
            size=1,
        )
        if existing_tasks:
            skipped += 1
            continue

        result = service.create_task(
            customer_id=payload["customer_id"],
            task_type=payload["task_type"],
            title=payload["title"],
            trigger_source=payload["trigger_source"],
            conversation_id=payload.get("conversation_id"),
            order_id=payload.get("order_id"),
            description=payload.get("description"),
            suggested_copy=payload.get("suggested_copy"),
            priority=payload.get("priority", "medium"),
            due_date=payload.get("due_date"),
            extra_json=payload.get("extra_json"),
        )
        if result:
            created.append(result)
        else:
            skipped += 1

    return {
        "created_tasks": created,
        "skipped": skipped,
    }
