from sqlalchemy import JSON, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class CustomerIdentityMapping(Base, TimestampMixin):
    __tablename__ = "customer_identity_mapping"
    __table_args__ = (
        UniqueConstraint("source_system", "platform", "account_id", "external_user_id", name="uq_customer_identity"),
        Index("ix_customer_identity_customer_id", "customer_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"), nullable=False)
    source_system: Mapped[str] = mapped_column(String(30), nullable=False, default="platform")
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    account_id: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    external_user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    external_user_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_primary: Mapped[bool] = mapped_column(nullable=False, default=False)
    extra_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
