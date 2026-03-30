from datetime import datetime

from sqlalchemy import JSON, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin

ALLOWED_EXCEPTION_TYPES = {"delay", "stockout", "address", "customs", "other"}
ALLOWED_EXCEPTION_STATUSES = {"open", "processing", "resolved", "cancelled"}


class OrderExceptionSnapshot(Base, TimestampMixin):
    __tablename__ = "order_exception_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(100), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    exception_type: Mapped[str] = mapped_column(String(30), nullable=False)
    exception_status: Mapped[str] = mapped_column(String(20), nullable=False)
    detail_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
