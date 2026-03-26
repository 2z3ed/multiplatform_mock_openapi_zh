from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from pydantic import BaseModel
from app.services.audit_service import audit_service

router = APIRouter(prefix="/api/audit-logs", tags=["audit"])


class AuditLogCreate(BaseModel):
    action: str
    actor_type: Optional[str] = "system"
    actor_id: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    detail: Optional[str] = None
    detail_json: Optional[dict] = None


@router.get("")
def get_audit_logs(
    action: Optional[str] = Query(None),
    user: Optional[str] = Query(None),
    limit: int = Query(100, le=500)
) -> dict:
    logs = audit_service.get_logs(
        action=action,
        actor_id=user,
        limit=limit
    )
    return {
        "total": len(logs),
        "items": logs
    }


@router.post("")
def create_audit_log(log: AuditLogCreate) -> dict:
    result = audit_service.log_event(
        action=log.action,
        actor_type=log.actor_type,
        actor_id=log.actor_id,
        target_type=log.target_type,
        target_id=log.target_id,
        detail=log.detail,
        detail_json=log.detail_json
    )
    return {"status": "ok", "log": result}