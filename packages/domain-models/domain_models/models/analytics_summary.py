from datetime import date, datetime
from typing import Optional

from sqlalchemy import JSON, Date, Integer
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class AnalyticsSummary(Base, TimestampMixin):
    __tablename__ = "analytics_summary"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    stat_date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    recommendation_created_count: Mapped[int] = mapped_column(Integer, default=0)
    recommendation_accepted_count: Mapped[int] = mapped_column(Integer, default=0)
    followup_executed_count: Mapped[int] = mapped_column(Integer, default=0)
    followup_closed_count: Mapped[int] = mapped_column(Integer, default=0)
    operation_campaign_completed_count: Mapped[int] = mapped_column(Integer, default=0)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
