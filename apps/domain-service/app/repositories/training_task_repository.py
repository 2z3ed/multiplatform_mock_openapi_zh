from typing import Optional
from sqlalchemy.orm import Session

from domain_models.models.training_task import TrainingTask, ALLOWED_TASK_TYPES, ALLOWED_TASK_STATUSES


class TrainingTaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        task_name: str,
        task_type: str,
        status: str = "pending",
        related_case_id: Optional[int] = None,
        detail_json: Optional[dict] = None
    ) -> TrainingTask:
        task = TrainingTask(
            task_name=task_name,
            task_type=task_type,
            status=status,
            related_case_id=related_case_id,
            detail_json=detail_json
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, id: int) -> Optional[TrainingTask]:
        return self.db.query(TrainingTask).filter(TrainingTask.id == id).first()

    def list_all(self) -> list[TrainingTask]:
        return self.db.query(TrainingTask).order_by(TrainingTask.created_at.desc()).all()

    def list_by_status(self, status: str) -> list[TrainingTask]:
        return (
            self.db.query(TrainingTask)
            .filter(TrainingTask.status == status)
            .order_by(TrainingTask.created_at.desc())
            .all()
        )

    def delete(self, id: int) -> bool:
        task = self.get_by_id(id)
        if task is None:
            return False
        self.db.delete(task)
        self.db.commit()
        return True
