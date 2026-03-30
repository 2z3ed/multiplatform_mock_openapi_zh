"""
Repository-level tests for order_audit_snapshot
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.order_audit_snapshot import OrderAuditSnapshot
from shared_db.base import Base
from app.repositories.order_audit_snapshot_repository import OrderAuditSnapshotRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestOrderAuditSnapshotRepository:
    """Test order_audit_snapshot repository"""

    def test_create_order_audit_snapshot(self, db_session):
        """Test creating order audit snapshot in database"""
        repo = OrderAuditSnapshotRepository(db_session)
        snapshot = repo.create(
            order_id="ORD001",
            platform="taobao",
            audit_status="approved"
        )

        assert snapshot.id is not None
        assert snapshot.order_id == "ORD001"
        assert snapshot.platform == "taobao"
        assert snapshot.audit_status == "approved"

    def test_create_with_audit_reason(self, db_session):
        """Test creating snapshot with audit reason"""
        repo = OrderAuditSnapshotRepository(db_session)
        snapshot = repo.create(
            order_id="ORD002",
            platform="jd",
            audit_status="rejected",
            audit_reason="地址信息不完整"
        )

        assert snapshot.id is not None
        assert snapshot.audit_status == "rejected"
        assert snapshot.audit_reason == "地址信息不完整"

    def test_get_by_id_exists(self, db_session):
        """Test getting existing snapshot by id"""
        repo = OrderAuditSnapshotRepository(db_session)
        created = repo.create(
            order_id="ORD001",
            platform="taobao",
            audit_status="approved"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent snapshot returns None"""
        repo = OrderAuditSnapshotRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_get_by_order_id(self, db_session):
        """Test getting snapshot by order_id"""
        repo = OrderAuditSnapshotRepository(db_session)
        repo.create(
            order_id="ORD001",
            platform="taobao",
            audit_status="pending",
            snapshot_at=datetime(2026, 3, 30, 12, 0, 0)
        )
        repo.create(
            order_id="ORD001",
            platform="taobao",
            audit_status="approved",
            snapshot_at=datetime(2026, 3, 30, 13, 0, 0)
        )

        result = repo.get_by_order_id("ORD001")
        assert result is not None
        assert result.audit_status == "approved"

    def test_list_all(self, db_session):
        """Test listing all snapshots"""
        repo = OrderAuditSnapshotRepository(db_session)
        repo.create(order_id="ORD001", platform="taobao", audit_status="approved")
        repo.create(order_id="ORD002", platform="jd", audit_status="pending")

        results = repo.list_all()
        assert len(results) == 2

    def test_list_by_order_id(self, db_session):
        """Test listing snapshots by order_id"""
        repo = OrderAuditSnapshotRepository(db_session)
        repo.create(order_id="ORD001", platform="taobao", audit_status="pending")
        repo.create(order_id="ORD001", platform="taobao", audit_status="approved")
        repo.create(order_id="ORD002", platform="jd", audit_status="approved")

        results = repo.list_by_order_id("ORD001")
        assert len(results) == 2

    def test_delete(self, db_session):
        """Test deleting snapshot"""
        repo = OrderAuditSnapshotRepository(db_session)
        created = repo.create(
            order_id="ORD001",
            platform="taobao",
            audit_status="approved"
        )

        success = repo.delete(created.id)
        assert success is True

        result = repo.get_by_id(created.id)
        assert result is None
