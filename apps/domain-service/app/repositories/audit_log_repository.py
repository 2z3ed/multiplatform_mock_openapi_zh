from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from domain_models.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        action: str,
        actor_type: str = "system",
        actor_id: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        detail: Optional[str] = None,
        detail_json: Optional[dict] = None
    ) -> AuditLog:
        log = AuditLog(
            action=action,
            actor_type=actor_type,
            actor_id=actor_id,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            detail_json=detail_json
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_logs(
        self,
        action: Optional[str] = None,
        actor_id: Optional[str] = None,
        target_id: Optional[str] = None,
        limit: int = 100
    ) -> list[AuditLog]:
        query = self.db.query(AuditLog)
        
        if action:
            query = query.filter(AuditLog.action == action)
        if actor_id:
            query = query.filter(AuditLog.actor_id == actor_id)
        if target_id:
            query = query.filter(AuditLog.target_id == target_id)
        
        return query.order_by(desc(AuditLog.created_at)).limit(limit).all()

    def get_by_id(self, log_id: int) -> Optional[AuditLog]:
        return self.db.query(AuditLog).filter(AuditLog.id == log_id).first()