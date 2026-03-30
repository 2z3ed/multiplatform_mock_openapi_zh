from datetime import date
from sqlalchemy import JSON, String, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin

ALLOWED_METRIC_TYPES = {
    "conversation_count",
    "avg_response_time",
    "satisfaction_score",
    "resolved_case_count"
}


class ManagementDashboardSnapshot(Base, TimestampMixin):
    __tablename__ = "management_dashboard_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_value: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    detail_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
