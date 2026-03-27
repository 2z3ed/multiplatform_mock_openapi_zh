from sqlalchemy import ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class CustomerTag(Base, TimestampMixin):
    __tablename__ = "customer_tag"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    tag_type: Mapped[str] = mapped_column(String(30), nullable=False)
    tag_value: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False, default="manual")
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
