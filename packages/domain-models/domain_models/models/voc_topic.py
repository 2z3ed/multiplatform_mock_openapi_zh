from sqlalchemy import JSON, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin

ALLOWED_TOPIC_TYPES = {"complaint", "feedback", "suggestion", "other"}
ALLOWED_SOURCES = {"conversation", "survey", "other"}


class VOCTopic(Base, TimestampMixin):
    __tablename__ = "voc_topic"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    topic_name: Mapped[str] = mapped_column(String(200), nullable=False)
    topic_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False)
    occurrence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
