from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class OperationCampaign(Base, TimestampMixin):
    __tablename__ = "operation_campaign"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    campaign_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_audience: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    content_template: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
