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

    def recommendation_created(
        self,
        recommendation_id: str,
        conversation_id: str,
        customer_id: str,
        product_id: str
    ) -> dict:
        """Log recommendation creation"""
        return self.log_event(
            action="recommendation_created",
            target_type="recommendation",
            target_id=recommendation_id,
            detail=f"Created recommendation for product: {product_id}",
            detail_json={
                "recommendation_id": recommendation_id,
                "conversation_id": conversation_id,
                "customer_id": customer_id,
                "product_id": product_id
            }
        )

    def recommendation_accepted(
        self,
        recommendation_id: str,
        conversation_id: str,
        customer_id: str,
        product_id: str
    ) -> dict:
        """Log recommendation accepted"""
        return self.log_event(
            action="recommendation_accepted",
            target_type="recommendation",
            target_id=recommendation_id,
            detail=f"Accepted recommendation for product: {product_id}",
            detail_json={
                "recommendation_id": recommendation_id,
                "conversation_id": conversation_id,
                "customer_id": customer_id,
                "product_id": product_id,
                "status": "accepted"
            }
        )

    def recommendation_rejected(
        self,
        recommendation_id: str,
        conversation_id: str,
        customer_id: str,
        product_id: str
    ) -> dict:
        """Log recommendation rejected"""
        return self.log_event(
            action="recommendation_rejected",
            target_type="recommendation",
            target_id=recommendation_id,
            detail=f"Rejected recommendation for product: {product_id}",
            detail_json={
                "recommendation_id": recommendation_id,
                "conversation_id": conversation_id,
                "customer_id": customer_id,
                "product_id": product_id,
                "status": "rejected"
            }
        )

    def customer_tag_created(
        self,
        tag_id: str,
        customer_id: str,
        tag_type: str,
        tag_value: str
    ) -> dict:
        """Log customer tag creation"""
        return self.log_event(
            action="customer_tag_created",
            target_type="customer_tag",
            target_id=tag_id,
            detail=f"Created tag: {tag_type}={tag_value}",
            detail_json={
                "tag_id": tag_id,
                "customer_id": customer_id,
                "tag_type": tag_type,
                "tag_value": tag_value
            }
        )

    def customer_tag_deleted(
        self,
        tag_id: str,
        customer_id: str,
        tag_type: str,
        tag_value: str
    ) -> dict:
        """Log customer tag deletion"""
        return self.log_event(
            action="customer_tag_deleted",
            target_type="customer_tag",
            target_id=tag_id,
            detail=f"Deleted tag: {tag_type}={tag_value}",
            detail_json={
                "tag_id": tag_id,
                "customer_id": customer_id,
                "tag_type": tag_type,
                "tag_value": tag_value
            }
        )

    def customer_profile_created(
        self,
        customer_id: str,
        total_orders: int,
        total_spent: str,
        avg_order_value: str
    ) -> dict:
        """Log customer profile creation"""
        return self.log_event(
            action="customer_profile_created",
            target_type="customer_profile",
            target_id=customer_id,
            detail=f"Created profile for customer: {customer_id}",
            detail_json={
                "customer_id": customer_id,
                "total_orders": total_orders,
                "total_spent": total_spent,
                "avg_order_value": avg_order_value
            }
        )

    def customer_profile_updated(
        self,
        customer_id: str,
        total_orders: int,
        total_spent: str,
        avg_order_value: str
    ) -> dict:
        """Log customer profile update"""
        return self.log_event(
            action="customer_profile_updated",
            target_type="customer_profile",
            target_id=customer_id,
            detail=f"Updated profile for customer: {customer_id}",
            detail_json={
                "customer_id": customer_id,
                "total_orders": total_orders,
                "total_spent": total_spent,
                "avg_order_value": avg_order_value
            }
        )

    def customer_profile_deleted(
        self,
        customer_id: str
    ) -> dict:
        """Log customer profile deletion"""
        return self.log_event(
            action="customer_profile_deleted",
            target_type="customer_profile",
            target_id=customer_id,
            detail=f"Deleted profile for customer: {customer_id}",
            detail_json={
                "customer_id": customer_id
            }
        )

    def followup_task_created(
        self,
        task_id: str,
        customer_id: str,
        conversation_id: str,
        order_id: str,
        task_type: str,
        status: str
    ) -> dict:
        """Log followup task creation"""
        return self.log_event(
            action="followup_task_created",
            target_type="followup_task",
            target_id=task_id,
            detail=f"Created followup task: {task_type}",
            detail_json={
                "task_id": task_id,
                "customer_id": customer_id,
                "conversation_id": conversation_id,
                "order_id": order_id,
                "task_type": task_type,
                "status": status
            }
        )

    def followup_task_updated(
        self,
        task_id: str,
        customer_id: str,
        conversation_id: str,
        order_id: str,
        task_type: str,
        status: str
    ) -> dict:
        """Log followup task update"""
        return self.log_event(
            action="followup_task_updated",
            target_type="followup_task",
            target_id=task_id,
            detail=f"Updated followup task: {task_type}",
            detail_json={
                "task_id": task_id,
                "customer_id": customer_id,
                "conversation_id": conversation_id,
                "order_id": order_id,
                "task_type": task_type,
                "status": status
            }
        )

    def followup_task_executed(
        self,
        task_id: str,
        customer_id: str,
        conversation_id: str,
        order_id: str,
        task_type: str,
        completed_by: str
    ) -> dict:
        """Log followup task execution"""
        return self.log_event(
            action="followup_task_executed",
            target_type="followup_task",
            target_id=task_id,
            detail=f"Executed followup task: {task_type}",
            detail_json={
                "task_id": task_id,
                "customer_id": customer_id,
                "conversation_id": conversation_id,
                "order_id": order_id,
                "task_type": task_type,
                "completed_by": completed_by
            }
        )

    def followup_task_closed(
        self,
        task_id: str,
        customer_id: str,
        conversation_id: str,
        order_id: str,
        task_type: str,
        completed_by: str
    ) -> dict:
        """Log followup task closure"""
        return self.log_event(
            action="followup_task_closed",
            target_type="followup_task",
            target_id=task_id,
            detail=f"Closed followup task: {task_type}",
            detail_json={
                "task_id": task_id,
                "customer_id": customer_id,
                "conversation_id": conversation_id,
                "order_id": order_id,
                "task_type": task_type,
                "completed_by": completed_by
            }
        )

    def operation_campaign_created(
        self,
        campaign_id: str,
        name: str,
        campaign_type: str
    ) -> dict:
        """Log operation campaign creation"""
        return self.log_event(
            action="operation_campaign_created",
            target_type="operation_campaign",
            target_id=campaign_id,
            detail=f"Created campaign: {name}",
            detail_json={
                "campaign_id": campaign_id,
                "name": name,
                "campaign_type": campaign_type,
                "status": "draft"
            }
        )

    def operation_campaign_updated(
        self,
        campaign_id: str,
        name: str,
        campaign_type: str
    ) -> dict:
        """Log operation campaign update"""
        return self.log_event(
            action="operation_campaign_updated",
            target_type="operation_campaign",
            target_id=campaign_id,
            detail=f"Updated campaign: {name}",
            detail_json={
                "campaign_id": campaign_id,
                "name": name,
                "campaign_type": campaign_type
            }
        )

    def operation_campaign_ready(
        self,
        campaign_id: str,
        name: str,
        campaign_type: str
    ) -> dict:
        """Log operation campaign marked as ready"""
        return self.log_event(
            action="operation_campaign_ready",
            target_type="operation_campaign",
            target_id=campaign_id,
            detail=f"Campaign ready: {name}",
            detail_json={
                "campaign_id": campaign_id,
                "name": name,
                "campaign_type": campaign_type,
                "status": "ready"
            }
        )

    def operation_campaign_completed(
        self,
        campaign_id: str,
        name: str,
        campaign_type: str
    ) -> dict:
        """Log operation campaign completion"""
        return self.log_event(
            action="operation_campaign_completed",
            target_type="operation_campaign",
            target_id=campaign_id,
            detail=f"Campaign completed: {name}",
            detail_json={
                "campaign_id": campaign_id,
                "name": name,
                "campaign_type": campaign_type,
                "status": "completed"
            }
        )

    def operation_campaign_cancelled(
        self,
        campaign_id: str,
        name: str,
        campaign_type: str
    ) -> dict:
        """Log operation campaign cancellation"""
        return self.log_event(
            action="operation_campaign_cancelled",
            target_type="operation_campaign",
            target_id=campaign_id,
            detail=f"Campaign cancelled: {name}",
            detail_json={
                "campaign_id": campaign_id,
                "name": name,
                "campaign_type": campaign_type,
                "status": "cancelled"
            }
        )

    def analytics_summary_generated(
        self,
        stat_date: str,
        recommendation_created_count: int,
        recommendation_accepted_count: int,
        followup_executed_count: int,
        followup_closed_count: int,
        operation_campaign_completed_count: int
    ) -> dict:
        """Log analytics summary generation"""
        return self.log_event(
            action="analytics_summary_generated",
            target_type="analytics_summary",
            target_id=stat_date,
            detail=f"Generated analytics summary for: {stat_date}",
            detail_json={
                "stat_date": stat_date,
                "recommendation_created_count": recommendation_created_count,
                "recommendation_accepted_count": recommendation_accepted_count,
                "followup_executed_count": followup_executed_count,
                "followup_closed_count": followup_closed_count,
                "operation_campaign_completed_count": operation_campaign_completed_count
            }
        )

    def risk_flag_created(
        self,
        risk_flag_id: str,
        customer_id: str,
        conversation_id: Optional[str],
        risk_type: str,
        risk_level: str
    ) -> dict:
        """Log risk flag creation"""
        return self.log_event(
            action="risk_flag_created",
            target_type="risk_flag",
            target_id=risk_flag_id,
            detail=f"Created risk flag: {risk_type}",
            detail_json={
                "risk_flag_id": risk_flag_id,
                "customer_id": customer_id,
                "conversation_id": conversation_id,
                "risk_type": risk_type,
                "risk_level": risk_level,
                "status": "active"
            }
        )

    def risk_flag_resolved(
        self,
        risk_flag_id: str,
        customer_id: str,
        conversation_id: Optional[str],
        risk_type: str,
        risk_level: str
    ) -> dict:
        """Log risk flag resolution"""
        return self.log_event(
            action="risk_flag_resolved",
            target_type="risk_flag",
            target_id=risk_flag_id,
            detail=f"Resolved risk flag: {risk_type}",
            detail_json={
                "risk_flag_id": risk_flag_id,
                "customer_id": customer_id,
                "conversation_id": conversation_id,
                "risk_type": risk_type,
                "risk_level": risk_level,
                "status": "resolved"
            }
        )

    def risk_flag_dismissed(
        self,
        risk_flag_id: str,
        customer_id: str,
        conversation_id: Optional[str],
        risk_type: str,
        risk_level: str
    ) -> dict:
        """Log risk flag dismissal"""
        return self.log_event(
            action="risk_flag_dismissed",
            target_type="risk_flag",
            target_id=risk_flag_id,
            detail=f"Dismissed risk flag: {risk_type}",
            detail_json={
                "risk_flag_id": risk_flag_id,
                "customer_id": customer_id,
                "conversation_id": conversation_id,
                "risk_type": risk_type,
                "risk_level": risk_level,
                "status": "dismissed"
            }
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