from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.repositories.followup_task_repository import FollowUpTaskRepository
from app.services.audit_service import AuditService


class FollowUpTaskService:
    """Follow-up task service for V2"""

    VALID_STATUSES = {"pending", "completed", "closed"}
    VALID_PRIORITIES = {"low", "medium", "high"}
    VALID_TASK_TYPES = {"consultation_no_order", "unpaid", "shipment_exception", "after_sale_care"}
    VALID_TRIGGER_SOURCES = {"manual", "ai_suggested"}

    ALLOWED_UPDATE_FIELDS = {
        "title", "description", "suggested_copy",
        "priority", "due_date", "extra_json"
    }

    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = FollowUpTaskRepository(db_session)
        self._audit_service = AuditService(db_session=db_session)

    def _to_dict(self, task) -> dict:
        return {
            "id": task.id,
            "conversation_id": task.conversation_id,
            "customer_id": task.customer_id,
            "order_id": task.order_id,
            "task_type": task.task_type,
            "trigger_source": task.trigger_source,
            "title": task.title,
            "description": task.description,
            "suggested_copy": task.suggested_copy,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "completed_by": task.completed_by,
            "extra_json": task.extra_json,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        }

    def _log_audit(self, task, action: str, extra_json: Optional[dict] = None):
        detail_json = {
            "task_id": str(task.id),
            "customer_id": str(task.customer_id),
            "conversation_id": str(task.conversation_id) if task.conversation_id else "",
            "order_id": task.order_id or "",
            "task_type": task.task_type,
            "status": task.status
        }
        if extra_json:
            detail_json.update(extra_json)
        
        if action == "followup_task_created":
            self._audit_service.followup_task_created(
                task_id=str(task.id),
                customer_id=str(task.customer_id),
                conversation_id=str(task.conversation_id) if task.conversation_id else "",
                order_id=task.order_id or "",
                task_type=task.task_type,
                status=task.status
            )
        elif action == "followup_task_updated":
            self._audit_service.followup_task_updated(
                task_id=str(task.id),
                customer_id=str(task.customer_id),
                conversation_id=str(task.conversation_id) if task.conversation_id else "",
                order_id=task.order_id or "",
                task_type=task.task_type,
                status=task.status
            )
        elif action == "followup_task_executed":
            self._audit_service.followup_task_executed(
                task_id=str(task.id),
                customer_id=str(task.customer_id),
                conversation_id=str(task.conversation_id) if task.conversation_id else "",
                order_id=task.order_id or "",
                task_type=task.task_type,
                completed_by=extra_json.get("completed_by", "") if extra_json else ""
            )
        elif action == "followup_task_closed":
            self._audit_service.followup_task_closed(
                task_id=str(task.id),
                customer_id=str(task.customer_id),
                conversation_id=str(task.conversation_id) if task.conversation_id else "",
                order_id=task.order_id or "",
                task_type=task.task_type,
                completed_by=extra_json.get("completed_by", "") if extra_json else ""
            )

    def get_task(self, task_id: int) -> Optional[dict]:
        task = self._repo.get_by_id(task_id)
        if task is None:
            return None
        return self._to_dict(task)

    def list_tasks(
        self,
        customer_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        priority: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> tuple[list[dict], int]:
        if status is not None and status not in self.VALID_STATUSES:
            return [], 0
        if priority is not None and priority not in self.VALID_PRIORITIES:
            return [], 0
        if task_type is not None and task_type not in self.VALID_TASK_TYPES:
            return [], 0

        tasks, total = self._repo.list_by_filters(
            customer_id=customer_id,
            conversation_id=conversation_id,
            status=status,
            task_type=task_type,
            priority=priority,
            page=page,
            size=size
        )
        return [self._to_dict(t) for t in tasks], total

    def create_task(
        self,
        customer_id: int,
        task_type: str,
        title: str,
        trigger_source: str = "manual",
        conversation_id: Optional[int] = None,
        order_id: Optional[str] = None,
        description: Optional[str] = None,
        suggested_copy: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[datetime] = None,
        extra_json: Optional[dict] = None
    ) -> Optional[dict]:
        if task_type not in self.VALID_TASK_TYPES:
            return None
        if priority not in self.VALID_PRIORITIES:
            return None
        if trigger_source not in self.VALID_TRIGGER_SOURCES:
            return None

        task = self._repo.create(
            customer_id=customer_id,
            task_type=task_type,
            title=title,
            trigger_source=trigger_source,
            conversation_id=conversation_id,
            order_id=order_id,
            description=description,
            suggested_copy=suggested_copy,
            priority=priority,
            due_date=due_date,
            extra_json=extra_json
        )
        
        self._log_audit(task, "followup_task_created")
        
        return self._to_dict(task)

    def update_task(self, task_id: int, updates: dict) -> Optional[dict]:
        filtered_updates = {k: v for k, v in updates.items() if k in self.ALLOWED_UPDATE_FIELDS}
        if not filtered_updates:
            return None

        if "priority" in filtered_updates and filtered_updates["priority"] not in self.VALID_PRIORITIES:
            return None

        task = self._repo.update(task_id, filtered_updates)
        if task is None:
            return None
        
        self._log_audit(task, "followup_task_updated")
        
        return self._to_dict(task)

    def execute_task(self, task_id: int, completed_by: str) -> Optional[dict]:
        task = self._repo.get_by_id(task_id)
        if task is None:
            return None
        if task.status != "pending":
            return None

        now = datetime.utcnow()
        result = self._repo.update(task_id, {
            "status": "completed",
            "completed_at": now,
            "completed_by": completed_by
        })
        if result is None:
            return None
        
        self._log_audit(result, "followup_task_executed", {"completed_by": completed_by})
        
        return self._to_dict(result)

    def close_task(self, task_id: int, completed_by: str) -> Optional[dict]:
        task = self._repo.get_by_id(task_id)
        if task is None:
            return None
        if task.status != "pending":
            return None

        now = datetime.utcnow()
        result = self._repo.update(task_id, {
            "status": "closed",
            "completed_at": now,
            "completed_by": completed_by
        })
        if result is None:
            return None
        
        self._log_audit(result, "followup_task_closed", {"completed_by": completed_by})
        
        return self._to_dict(result)
