"""
Repository-level tests for management_dashboard_snapshot
"""

import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.management_dashboard_snapshot import ManagementDashboardSnapshot, ALLOWED_METRIC_TYPES
from shared_db.base import Base
from app.repositories.management_dashboard_snapshot_repository import ManagementDashboardSnapshotRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestManagementDashboardSnapshotRepository:
    """Test management_dashboard_snapshot repository"""

    def test_create_snapshot(self, db_session):
        """Test creating dashboard snapshot in database"""
        repo = ManagementDashboardSnapshotRepository(db_session)
        snapshot = repo.create(
            snapshot_date=date(2026, 3, 30),
            metric_type="conversation_count",
            metric_value=1250.0
        )

        assert snapshot.id is not None
        assert snapshot.snapshot_date == date(2026, 3, 30)
        assert snapshot.metric_type == "conversation_count"
        assert float(snapshot.metric_value) == 1250.0

    def test_create_all_metric_types(self, db_session):
        """Test creating snapshots with all allowed metric types"""
        repo = ManagementDashboardSnapshotRepository(db_session)
        
        for metric_type in ALLOWED_METRIC_TYPES:
            snapshot = repo.create(
                snapshot_date=date(2026, 3, 30),
                metric_type=metric_type,
                metric_value=100.0
            )
            assert snapshot.metric_type == metric_type

    def test_get_by_id_exists(self, db_session):
        """Test getting existing snapshot by id"""
        repo = ManagementDashboardSnapshotRepository(db_session)
        created = repo.create(
            snapshot_date=date(2026, 3, 30),
            metric_type="conversation_count",
            metric_value=100.0
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent snapshot returns None"""
        repo = ManagementDashboardSnapshotRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_list_all(self, db_session):
        """Test listing all snapshots"""
        repo = ManagementDashboardSnapshotRepository(db_session)
        repo.create(snapshot_date=date(2026, 3, 30), metric_type="conversation_count", metric_value=100.0)
        repo.create(snapshot_date=date(2026, 3, 29), metric_type="avg_response_time", metric_value=45.0)

        results = repo.list_all()
        assert len(results) == 2

    def test_list_by_metric_type(self, db_session):
        """Test listing snapshots by metric_type"""
        repo = ManagementDashboardSnapshotRepository(db_session)
        repo.create(snapshot_date=date(2026, 3, 30), metric_type="conversation_count", metric_value=100.0)
        repo.create(snapshot_date=date(2026, 3, 29), metric_type="conversation_count", metric_value=90.0)
        repo.create(snapshot_date=date(2026, 3, 30), metric_type="avg_response_time", metric_value=45.0)

        results = repo.list_by_metric_type("conversation_count")
        assert len(results) == 2

    def test_list_by_date(self, db_session):
        """Test listing snapshots by date"""
        repo = ManagementDashboardSnapshotRepository(db_session)
        repo.create(snapshot_date=date(2026, 3, 30), metric_type="conversation_count", metric_value=100.0)
        repo.create(snapshot_date=date(2026, 3, 30), metric_type="avg_response_time", metric_value=45.0)
        repo.create(snapshot_date=date(2026, 3, 29), metric_type="conversation_count", metric_value=90.0)

        results = repo.list_by_date(date(2026, 3, 30))
        assert len(results) == 2

    def test_delete(self, db_session):
        """Test deleting snapshot"""
        repo = ManagementDashboardSnapshotRepository(db_session)
        created = repo.create(
            snapshot_date=date(2026, 3, 30),
            metric_type="conversation_count",
            metric_value=100.0
        )

        success = repo.delete(created.id)
        assert success is True

        result = repo.get_by_id(created.id)
        assert result is None
