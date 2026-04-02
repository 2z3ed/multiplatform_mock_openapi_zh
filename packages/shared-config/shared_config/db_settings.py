from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


_project_root = Path(__file__).parent.parent.parent.parent
_env_file = _project_root / ".env"


class DatabaseSettings(BaseSettings):
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_db: str = "omni_csx"
    postgres_user: str = "omni"
    postgres_password: str = "omni"

    model_config = SettingsConfigDict(
        env_file=str(_env_file),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def sqlalchemy_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


db_settings = DatabaseSettings()
