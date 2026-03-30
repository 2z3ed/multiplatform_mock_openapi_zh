from datetime import datetime

from sqlalchemy import JSON, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin

ALLOWED_AUDIT_STATUSES = {"pending", "approved", "rejected"}


class OrderAuditSnapshot(Base, TimestampMixin):
    __tablename__ = "order_audit_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(String(100), nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    audit_status: Mapped[str] = mapped_column(String(20), nullable=False)
    audit_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
