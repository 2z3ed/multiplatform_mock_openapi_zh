from sqlalchemy import JSON, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin

ALLOWED_TASK_TYPES = {"review", "practice", "quiz", "other"}
ALLOWED_TASK_STATUSES = {"pending", "in_progress", "completed", "cancelled"}


class TrainingTask(Base, TimestampMixin):
    __tablename__ = "training_task"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_name: Mapped[str] = mapped_column(String(200), nullable=False)
    task_type: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    related_case_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("training_case.id"), nullable=True)
    detail_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
