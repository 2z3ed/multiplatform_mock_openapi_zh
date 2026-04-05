from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class Customer(Base, TimestampMixin):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    platform_customer_id: Mapped[str] = mapped_column(String(100), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    raw_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    conversations = relationship("Conversation", back_populates="customer")
