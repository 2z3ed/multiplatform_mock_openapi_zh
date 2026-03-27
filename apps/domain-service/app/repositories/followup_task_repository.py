from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.follow_up_task import FollowUpTask


class FollowUpTaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: int) -> Optional[FollowUpTask]:
        return self.db.query(FollowUpTask).filter(FollowUpTask.id == task_id).first()

    def list_by_filters(
        self,
        customer_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        priority: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> tuple[list[FollowUpTask], int]:
        if page < 1:
            page = 1
        if size > 100:
            size = 100
        if size < 1:
            size = 20

        offset = (page - 1) * size
        query = self.db.query(FollowUpTask)

        if customer_id is not None:
            query = query.filter(FollowUpTask.customer_id == customer_id)
        if conversation_id is not None:
            query = query.filter(FollowUpTask.conversation_id == conversation_id)
        if status is not None:
            query = query.filter(FollowUpTask.status == status)
        if task_type is not None:
            query = query.filter(FollowUpTask.task_type == task_type)
        if priority is not None:
            query = query.filter(FollowUpTask.priority == priority)

        total = query.count()
        results = query.order_by(FollowUpTask.created_at.desc()).offset(offset).limit(size).all()
        return results, total

    def create(
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
    ) -> FollowUpTask:
        task = FollowUpTask(
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
            extra_json=extra_json,
            status="pending"
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(
        self,
        task_id: int,
        updates: dict
    ) -> Optional[FollowUpTask]:
        """
        采用最小 patch 语义：
        - updates 是一个字典，key 为要更新的字段名
        - 只更新传入的 key，即使 value 为 None 也会更新为 None
        - 未传入的 key 不做任何修改
        """
        task = self.get_by_id(task_id)
        if task is None:
            return None

        for field_name, field_value in updates.items():
            if hasattr(task, field_name):
                setattr(task, field_name, field_value)

        self.db.commit()
        self.db.refresh(task)
        return task
