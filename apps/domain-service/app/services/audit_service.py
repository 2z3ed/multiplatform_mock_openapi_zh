"""
Audit service for V1

Records all required audit events:
- platform config updated
- provider mode switched
- document uploaded
- knowledge reindexed
- AI suggestion generated
- message sent by agent
- conversation handed off
- conversation assigned
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    """Audit service for V1 - DB-backed"""

    def __init__(self, db_session: Optional[Session] = None):
        self._db_session = db_session
        self._repo: Optional[AuditLogRepository] = None

    def _get_repo(self) -> AuditLogRepository:
        if self._repo is None:
            if self._db_session is None:
                from shared_db import get_db
                self._db_session = next(get_db())
            self._repo = AuditLogRepository(self._db_session)
        return self._repo

    def log_event(
        self,
        action: str,
        actor_type: Optional[str] = "system",
        actor_id: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        detail: Optional[str] = None,
        detail_json: Optional[dict] = None
    ) -> dict:
        """Log an audit event to database"""
        repo = self._get_repo()
        log_entry = repo.create(
            action=action,
            actor_type=actor_type or "system",
            actor_id=actor_id,
            target_type=target_type,
            target_id=target_id,
            detail=detail,
            detail_json=detail_json
        )
        return {
            "id": log_entry.id,
            "actor_type": log_entry.actor_type,
            "actor_id": log_entry.actor_id,
            "action": log_entry.action,
            "target_type": log_entry.target_type,
            "target_id": log_entry.target_id,
            "detail": log_entry.detail,
            "detail_json": log_entry.detail_json,
            "created_at": log_entry.created_at.isoformat() if log_entry.created_at else None,
            "updated_at": log_entry.updated_at.isoformat() if log_entry.updated_at else None,
        }

    def get_logs(
        self,
        action: Optional[str] = None,
        actor_id: Optional[str] = None,
        target_id: Optional[str] = None,
        limit: int = 100
    ) -> list[dict]:
        """Get audit logs with optional filters"""
        repo = self._get_repo()
        logs = repo.get_logs(
            action=action,
            actor_id=actor_id,
            target_id=target_id,
            limit=limit
        )
        return [{
            "id": log.id,
            "actor_type": log.actor_type,
            "actor_id": log.actor_id,
            "action": log.action,
            "target_type": log.target_type,
            "target_id": log.target_id,
            "detail": log.detail,
            "detail_json": log.detail_json,
            "created_at": log.created_at.isoformat() if log.created_at else None,
            "updated_at": log.updated_at.isoformat() if log.updated_at else None,
        } for log in logs]

    def platform_config_updated(self, platform: str, config: dict) -> dict:
        """Log platform config update"""
        return self.log_event(
            action="platform_config_updated",
            target_type="platform",
            target_id=platform,
            detail=f"Updated platform config: {platform}",
            detail_json=config
        )

    def provider_mode_switched(self, platform: str, old_mode: str, new_mode: str) -> dict:
        """Log provider mode switch"""
        return self.log_event(
            action="provider_mode_switched",
            target_type="platform",
            target_id=platform,
            detail=f"Switched from {old_mode} to {new_mode}",
            detail_json={"old_mode": old_mode, "new_mode": new_mode}
        )

    def document_uploaded(self, document_id: str, title: str, user: str = "admin") -> dict:
        """Log document upload"""
        return self.log_event(
            action="document_uploaded",
            actor_type="user",
            actor_id=user,
            target_type="document",
            target_id=document_id,
            detail=f"Uploaded document: {title}"
        )

    def knowledge_reindexed(self, total_documents: int, total_chunks: int) -> dict:
        """Log knowledge reindex"""
        return self.log_event(
            action="knowledge_reindexed",
            detail=f"Reindexed {total_documents} documents, {total_chunks} chunks",
            detail_json={"total_documents": total_documents, "total_chunks": total_chunks}
        )

    def ai_suggestion_generated(
        self,
        conversation_id: str,
        intent: str,
        agent_id: str = "system"
    ) -> dict:
        """Log AI suggestion generation"""
        return self.log_event(
            action="ai_suggestion_generated",
            actor_type="ai",
            actor_id=agent_id,
            target_type="conversation",
            target_id=conversation_id,
            detail=f"Generated suggestion for intent: {intent}",
            detail_json={"intent": intent}
        )

    def message_sent(
        self,
        conversation_id: str,
        message_id: str,
        agent_id: str
    ) -> dict:
        """Log message sent by agent"""
        return self.log_event(
            action="message_sent",
            actor_type="agent",
            actor_id=agent_id,
            target_type="message",
            target_id=message_id,
            detail=f"Sent message in conversation: {conversation_id}",
            detail_json={"conversation_id": conversation_id}
        )

    def conversation_assigned(
        self,
        conversation_id: str,
        agent_id: str,
        assigned_by: str = "system"
    ) -> dict:
        """Log conversation assignment"""
        return self.log_event(
            action="conversation_assigned",
            actor_type="system",
            actor_id=assigned_by,
            target_type="conversation",
            target_id=conversation_id,
            detail=f"Assigned conversation to agent: {agent_id}",
            detail_json={"assigned_agent": agent_id}
        )

    def conversation_handed_off(
        self,
        conversation_id: str,
        from_agent: str,
        to_agent: str
    ) -> dict:
        """Log conversation handoff"""
        return self.log_event(
            action="conversation_handed_off",
            actor_type="agent",
            actor_id=from_agent,
            target_type="conversation",
            target_id=conversation_id,
            detail=f"Handoff from {from_agent} to {to_agent}",
            detail_json={"from_agent": from_agent, "to_agent": to_agent}
        )


_audit_service_instance: Optional[AuditService] = None


def get_audit_service(db: Session = None) -> AuditService:
    """Dependency injection for audit service"""
    global _audit_service_instance
    if db is not None:
        return AuditService(db_session=db)
    if _audit_service_instance is None:
        _audit_service_instance = AuditService()
    return _audit_service_instance


audit_service = AuditService()