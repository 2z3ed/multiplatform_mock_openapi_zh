from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class OperationCampaign(Base, TimestampMixin):
    __tablename__ = "operation_campaign"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    campaign_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    audience_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    preview_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
