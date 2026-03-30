"""
Repository-level tests for erp_inventory_snapshot
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.erp_inventory_snapshot import ERPInventorySnapshot
from shared_db.base import Base
from app.repositories.erp_inventory_snapshot_repository import ERPInventorySnapshotRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestERPInventorySnapshotRepository:
    """Test erp_inventory_snapshot repository"""

    def test_create_inventory_snapshot(self, db_session):
        """Test creating inventory snapshot in database"""
        repo = ERPInventorySnapshotRepository(db_session)
        snapshot = repo.create(
            sku_code="SKU001",
            warehouse_code="WH-BJ",
            available_qty=100,
            reserved_qty=10,
            status="normal"
        )

        assert snapshot.id is not None
        assert snapshot.sku_code == "SKU001"
        assert snapshot.warehouse_code == "WH-BJ"
        assert snapshot.available_qty == 100
        assert snapshot.reserved_qty == 10
        assert snapshot.status == "normal"

    def test_create_with_minimal_fields(self, db_session):
        """Test creating inventory snapshot with minimal fields"""
        repo = ERPInventorySnapshotRepository(db_session)
        snapshot = repo.create(
            sku_code="SKU002",
            warehouse_code="WH-SH",
            available_qty=50
        )

        assert snapshot.id is not None
        assert snapshot.reserved_qty == 0
        assert snapshot.status == "normal"
        assert snapshot.source_json is None

    def test_get_by_id_exists(self, db_session):
        """Test getting existing snapshot by id"""
        repo = ERPInventorySnapshotRepository(db_session)
        created = repo.create(
            sku_code="SKU001",
            warehouse_code="WH-BJ",
            available_qty=100
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent snapshot returns None"""
        repo = ERPInventorySnapshotRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_get_by_sku_code(self, db_session):
        """Test getting snapshot by sku_code"""
        repo = ERPInventorySnapshotRepository(db_session)
        repo.create(
            sku_code="SKU001",
            warehouse_code="WH-BJ",
            available_qty=100,
            snapshot_at=datetime(2026, 3, 30, 12, 0, 0)
        )
        repo.create(
            sku_code="SKU001",
            warehouse_code="WH-SH",
            available_qty=50,
            snapshot_at=datetime(2026, 3, 30, 13, 0, 0)
        )

        result = repo.get_by_sku_code("SKU001")
        assert result is not None
        assert result.warehouse_code == "WH-SH"

    def test_list_all(self, db_session):
        """Test listing all snapshots"""
        repo = ERPInventorySnapshotRepository(db_session)
        repo.create(sku_code="SKU001", warehouse_code="WH-BJ", available_qty=100)
        repo.create(sku_code="SKU002", warehouse_code="WH-SH", available_qty=50)

        results = repo.list_all()
        assert len(results) == 2

    def test_list_by_sku_code(self, db_session):
        """Test listing snapshots by sku_code"""
        repo = ERPInventorySnapshotRepository(db_session)
        repo.create(sku_code="SKU001", warehouse_code="WH-BJ", available_qty=100)
        repo.create(sku_code="SKU001", warehouse_code="WH-SH", available_qty=50)
        repo.create(sku_code="SKU002", warehouse_code="WH-GZ", available_qty=200)

        results = repo.list_by_sku_code("SKU001")
        assert len(results) == 2

    def test_delete(self, db_session):
        """Test deleting snapshot"""
        repo = ERPInventorySnapshotRepository(db_session)
        created = repo.create(
            sku_code="SKU001",
            warehouse_code="WH-BJ",
            available_qty=100
        )

        success = repo.delete(created.id)
        assert success is True

        result = repo.get_by_id(created.id)
        assert result is None
