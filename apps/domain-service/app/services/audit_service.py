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


class AuditService:
    """Simple in-memory audit log service for V1"""

    def __init__(self):
        self._logs: list[dict] = []

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
        """Log an audit event"""
        log_entry = {
            "id": f"log_{len(self._logs) + 1:05d}",
            "actor_type": actor_type or "system",
            "actor_id": actor_id,
            "action": action,
            "target_type": target_type,
            "target_id": target_id,
            "detail": detail,
            "detail_json": detail_json or {},
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }
        self._logs.append(log_entry)
        return log_entry

    def get_logs(
        self,
        action: Optional[str] = None,
        actor_id: Optional[str] = None,
        target_id: Optional[str] = None,
        limit: int = 100
    ) -> list[dict]:
        """Get audit logs with optional filters"""
        logs = self._logs
        if action:
            logs = [l for l in logs if l["action"] == action]
        if actor_id:
            logs = [l for l in logs if l["actor_id"] == actor_id]
        if target_id:
            logs = [l for l in logs if l["target_id"] == target_id]
        return logs[-limit:]

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


audit_service = AuditService()