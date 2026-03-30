from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class QualityAlert(Base, TimestampMixin):
    __tablename__ = "quality_alert"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    quality_inspection_result_id: Mapped[int] = mapped_column(
        ForeignKey("quality_inspection_result.id"), unique=True, nullable=False
    )
    alert_level: Mapped[str] = mapped_column(String(20), nullable=False, default="high")
