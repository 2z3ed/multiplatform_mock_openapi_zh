from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin

ALLOWED_SYNC_STATUSES = {"success", "failed", "partial"}
ALLOWED_TRIGGER_TYPES = {"manual", "scheduled", "api"}
ALLOWED_PROVIDER_MODES = {"mock", "real"}


class IntegrationSyncStatus(Base, TimestampMixin):
    __tablename__ = "integration_sync_status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    trigger_type: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    provider_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="mock")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success")
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    inventory_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    audit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    exception_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
