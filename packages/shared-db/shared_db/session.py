from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from shared_config.db_settings import db_settings

engine = create_engine(db_settings.sqlalchemy_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
