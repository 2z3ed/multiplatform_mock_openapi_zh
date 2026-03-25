from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from shared_db.base import Base
from shared_db.mixins import TimestampMixin


class PlatformAccount(Base, TimestampMixin):
    __tablename__ = "platform_account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    account_name: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="mock")
    config_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
