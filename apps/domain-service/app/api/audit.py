from fastapi import APIRouter, Query
from typing import Optional
from app.services.audit_service import audit_service

router = APIRouter(prefix="/api/audit-logs", tags=["audit"])


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