from datetime import datetime
from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class FollowUpTask(Base, TimestampMixin):
    """
    跟单任务模型
    
    约束说明:
    - customer_id: 必填，确保每条任务归属明确客户
    - conversation_id/order_id: 可空，支持纯客户维度的跟单任务
    - trigger_source: 本轮仅实现 manual，ai_suggested 预留供后续扩展
    - task_type: 咨询未下单(consultation_no_order)/未付款(unpaid)/发货异常(shipment_exception)/售后关怀(after_sale_care)
    - status: pending(待执行)/in_progress(执行中)/completed(已完成)/closed(已关闭)
    - priority: low(低)/medium(中)/high(高)
    """
    __tablename__ = "follow_up_task"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    conversation_id: Mapped[int | None] = mapped_column(ForeignKey("conversation.id"), nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    order_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    task_type: Mapped[str] = mapped_column(String(30), nullable=False)
    trigger_source: Mapped[str] = mapped_column(String(30), nullable=False, default="manual")
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_copy: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    due_date: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    completed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
