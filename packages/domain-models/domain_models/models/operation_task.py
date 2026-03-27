from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class OperationTask(Base, TimestampMixin):
    __tablename__ = "operation_task"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    campaign_id: Mapped[int | None] = mapped_column(ForeignKey("operation_campaign.id"), nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    task_type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    scheduled_at: Mapped[str | None] = mapped_column(String(20), nullable=True)
    executed_at: Mapped[str | None] = mapped_column(String(20), nullable=True)
    executed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
