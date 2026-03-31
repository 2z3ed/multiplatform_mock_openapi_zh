"""
Tests for Snapshot Cleanup functionality.
"""

import os
import sys
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared_db.base import Base
from domain_models.models import (
    ERPInventorySnapshot,
    OrderAuditSnapshot,
    OrderExceptionSnapshot,
    IntegrationSyncStatus,
)

from app.repositories.erp_inventory_snapshot_repository import ERPInventorySnapshotRepository
from app.repositories.order_audit_snapshot_repository import OrderAuditSnapshotRepository
from app.repositories.order_exception_snapshot_repository import OrderExceptionSnapshotRepository
from app.repositories.integration_sync_status_repository import IntegrationSyncStatusRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestInventoryCleanup:
    """Test inventory snapshot cleanup."""

    def test_cleanup_dry_run_default(self, db_session):
        """Test dry-run default does no actual deletion."""
        repo = ERPInventorySnapshotRepository(db_session)
        
        for i in range(10):
            repo.create(
                sku_code=f"SKU-{i}",
                warehouse_code=f"WH-{i}",
                available_qty=100,
                snapshot_at=datetime.utcnow() - timedelta(days=30),
            )
        
        result = repo.cleanup_old_snapshots(retention_days=7, dry_run=True)
        
        assert result["to_delete_count"] == 9
        assert result["deleted_count"] == 0
        assert db_session.query(ERPInventorySnapshot).count() == 10

    def test_cleanup_execute_required(self, db_session):
        """Test --execute is required for actual deletion."""
        repo = ERPInventorySnapshotRepository(db_session)
        
        for i in range(10):
            repo.create(
                sku_code=f"SKU-{i}",
                warehouse_code=f"WH-{i}",
                available_qty=100,
                snapshot_at=datetime.utcnow() - timedelta(days=30),
            )
        
        result = repo.cleanup_old_snapshots(retention_days=7, dry_run=False)
        
        assert result["to_delete_count"] == 9
        assert result["deleted_count"] == 9
        assert db_session.query(ERPInventorySnapshot).count() == 1

    def test_cleanup_retention_days(self, db_session):
        """Test retention_days parameter works."""
        repo = ERPInventorySnapshotRepository(db_session)
        
        for i in range(5):
            repo.create(
                sku_code=f"SKU-{i}",
                warehouse_code=f"WH-{i}",
                available_qty=100,
                snapshot_at=datetime.utcnow() - timedelta(days=30),
            )
        
        for i in range(5):
            repo.create(
                sku_code=f"SKU-NEW-{i}",
                warehouse_code=f"WH-{i}",
                available_qty=100,
                snapshot_at=datetime.utcnow() - timedelta(days=3),
            )
        
        result = repo.cleanup_old_snapshots(retention_days=7, dry_run=False)
        
        assert result["to_delete_count"] == 5
        assert result["deleted_count"] == 5
        assert db_session.query(ERPInventorySnapshot).count() == 5

    def test_cleanup_type_inventory_only(self, db_session):
        """Test cleanup only affects inventory snapshots."""
        inventory_repo = ERPInventorySnapshotRepository(db_session)
        audit_repo = OrderAuditSnapshotRepository(db_session)
        
        for i in range(5):
            inventory_repo.create(
                sku_code=f"SKU-{i}",
                warehouse_code=f"WH-{i}",
                available_qty=100,
                snapshot_at=datetime.utcnow() - timedelta(days=10),
            )
        
        for i in range(5):
            audit_repo.create(
                order_id=f"ORDER-{i}",
                platform="test",
                audit_status="pending",
                snapshot_at=datetime.utcnow() - timedelta(days=10),
            )
        
        result = inventory_repo.cleanup_old_snapshots(retention_days=7, dry_run=False)
        
        assert result["deleted_count"] == 4
        assert db_session.query(ERPInventorySnapshot).count() == 1
        assert db_session.query(OrderAuditSnapshot).count() == 5


class TestAuditCleanup:
    """Test order audit snapshot cleanup."""

    def test_cleanup_type_audit_only(self, db_session):
        """Test cleanup only affects audit snapshots."""
        audit_repo = OrderAuditSnapshotRepository(db_session)
        inventory_repo = ERPInventorySnapshotRepository(db_session)
        
        for i in range(5):
            audit_repo.create(
                order_id=f"ORDER-{i}",
                platform="test",
                audit_status="pending",
                snapshot_at=datetime.utcnow() - timedelta(days=10),
            )
        
        for i in range(5):
            inventory_repo.create(
                sku_code=f"SKU-{i}",
                warehouse_code=f"WH-{i}",
                available_qty=100,
                snapshot_at=datetime.utcnow() - timedelta(days=10),
            )
        
        result = audit_repo.cleanup_old_snapshots(retention_days=7, dry_run=False)
        
        assert result["deleted_count"] == 4
        assert db_session.query(OrderAuditSnapshot).count() == 1
        assert db_session.query(ERPInventorySnapshot).count() == 5


class TestExceptionCleanup:
    """Test order exception snapshot cleanup."""

    def test_cleanup_type_exception_only(self, db_session):
        """Test cleanup only affects exception snapshots."""
        exception_repo = OrderExceptionSnapshotRepository(db_session)
        inventory_repo = ERPInventorySnapshotRepository(db_session)
        
        for i in range(5):
            exception_repo.create(
                order_id=f"ORDER-{i}",
                platform="test",
                exception_type="delay",
                exception_status="open",
                snapshot_at=datetime.utcnow() - timedelta(days=10),
            )
        
        for i in range(5):
            inventory_repo.create(
                sku_code=f"SKU-{i}",
                warehouse_code=f"WH-{i}",
                available_qty=100,
                snapshot_at=datetime.utcnow() - timedelta(days=10),
            )
        
        result = exception_repo.cleanup_old_snapshots(retention_days=7, dry_run=False)
        
        assert result["deleted_count"] == 4
        assert db_session.query(OrderExceptionSnapshot).count() == 1
        assert db_session.query(ERPInventorySnapshot).count() == 5


class TestIntegrationSyncStatusNotCleaned:
    """Test IntegrationSyncStatus is not cleaned up."""

    def test_sync_status_not_affected(self, db_session):
        """Test that IntegrationSyncStatus is not affected by cleanup."""
        sync_repo = IntegrationSyncStatusRepository(db_session)
        inventory_repo = ERPInventorySnapshotRepository(db_session)
        
        sync_repo.create(
            trigger_type="manual",
            provider_mode="mock",
            started_at=datetime.utcnow() - timedelta(days=30),
        )
        
        for i in range(5):
            inventory_repo.create(
                sku_code=f"SKU-{i}",
                warehouse_code=f"WH-{i}",
                available_qty=100,
                snapshot_at=datetime.utcnow() - timedelta(days=30),
            )
        
        result = inventory_repo.cleanup_old_snapshots(retention_days=7, dry_run=False)
        
        assert result["deleted_count"] == 4
        assert db_session.query(IntegrationSyncStatus).count() == 1
        assert db_session.query(ERPInventorySnapshot).count() == 1
