"""
Repository-level tests for order_exception_snapshot
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.order_exception_snapshot import OrderExceptionSnapshot
from shared_db.base import Base
from app.repositories.order_exception_snapshot_repository import OrderExceptionSnapshotRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestOrderExceptionSnapshotRepository:
    """Test order_exception_snapshot repository"""

    def test_create_order_exception_snapshot(self, db_session):
        """Test creating order exception snapshot in database"""
        repo = OrderExceptionSnapshotRepository(db_session)
        snapshot = repo.create(
            order_id="ORD001",
            platform="taobao",
            exception_type="delay",
            exception_status="open"
        )

        assert snapshot.id is not None
        assert snapshot.order_id == "ORD001"
        assert snapshot.platform == "taobao"
        assert snapshot.exception_type == "delay"
        assert snapshot.exception_status == "open"

    def test_create_with_detail_json(self, db_session):
        """Test creating snapshot with detail_json"""
        repo = OrderExceptionSnapshotRepository(db_session)
        snapshot = repo.create(
            order_id="ORD002",
            platform="jd",
            exception_type="stockout",
            exception_status="processing",
            detail_json={"expected_restock": "2026-04-05"}
        )

        assert snapshot.id is not None
        assert snapshot.exception_type == "stockout"
        assert snapshot.detail_json == {"expected_restock": "2026-04-05"}

    def test_get_by_id_exists(self, db_session):
        """Test getting existing snapshot by id"""
        repo = OrderExceptionSnapshotRepository(db_session)
        created = repo.create(
            order_id="ORD001",
            platform="taobao",
            exception_type="delay",
            exception_status="open"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent snapshot returns None"""
        repo = OrderExceptionSnapshotRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_get_by_order_id(self, db_session):
        """Test getting snapshot by order_id"""
        repo = OrderExceptionSnapshotRepository(db_session)
        repo.create(
            order_id="ORD001",
            platform="taobao",
            exception_type="delay",
            exception_status="open",
            snapshot_at=datetime(2026, 3, 30, 12, 0, 0)
        )
        repo.create(
            order_id="ORD001",
            platform="taobao",
            exception_type="delay",
            exception_status="resolved",
            snapshot_at=datetime(2026, 3, 30, 13, 0, 0)
        )

        result = repo.get_by_order_id("ORD001")
        assert result is not None
        assert result.exception_status == "resolved"

    def test_list_all(self, db_session):
        """Test listing all snapshots"""
        repo = OrderExceptionSnapshotRepository(db_session)
        repo.create(order_id="ORD001", platform="taobao", exception_type="delay", exception_status="open")
        repo.create(order_id="ORD002", platform="jd", exception_type="stockout", exception_status="processing")

        results = repo.list_all()
        assert len(results) == 2

    def test_list_by_order_id(self, db_session):
        """Test listing snapshots by order_id"""
        repo = OrderExceptionSnapshotRepository(db_session)
        repo.create(order_id="ORD001", platform="taobao", exception_type="delay", exception_status="open")
        repo.create(order_id="ORD001", platform="taobao", exception_type="delay", exception_status="resolved")
        repo.create(order_id="ORD002", platform="jd", exception_type="stockout", exception_status="processing")

        results = repo.list_by_order_id("ORD001")
        assert len(results) == 2

    def test_list_by_exception_type(self, db_session):
        """Test listing snapshots by exception_type"""
        repo = OrderExceptionSnapshotRepository(db_session)
        repo.create(order_id="ORD001", platform="taobao", exception_type="delay", exception_status="open")
        repo.create(order_id="ORD002", platform="jd", exception_type="delay", exception_status="processing")
        repo.create(order_id="ORD003", platform="pdd", exception_type="stockout", exception_status="open")

        results = repo.list_by_exception_type("delay")
        assert len(results) == 2

    def test_delete(self, db_session):
        """Test deleting snapshot"""
        repo = OrderExceptionSnapshotRepository(db_session)
        created = repo.create(
            order_id="ORD001",
            platform="taobao",
            exception_type="delay",
            exception_status="open"
        )

        success = repo.delete(created.id)
        assert success is True

        result = repo.get_by_id(created.id)
        assert result is None
