"""
Tests for Integration Scheduler.
"""

import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared_db.base import Base
from domain_models.models import IntegrationSyncStatus


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestSchedulerConfiguration:
    """Test scheduler configuration"""

    def test_scheduled_refresh_disabled_by_default(self, monkeypatch):
        """Test scheduled refresh is disabled by default"""
        from app.scheduler.integration_scheduler import _get_config
        
        monkeypatch.delenv("ODOO_SCHEDULED_REFRESH_ENABLED", raising=False)
        monkeypatch.delenv("ODOO_PROVIDER_MODE", raising=False)
        
        enabled, provider_mode, inventory_interval, audit_interval = _get_config()
        
        assert enabled is False
        assert provider_mode == "mock"

    def test_scheduled_refresh_not_started_in_mock_mode(self, monkeypatch):
        """Test scheduler does not start in mock mode"""
        from app.scheduler.integration_scheduler import start_scheduler, stop_scheduler, is_scheduler_running
        
        monkeypatch.setenv("ODOO_PROVIDER_MODE", "mock")
        monkeypatch.setenv("ODOO_SCHEDULED_REFRESH_ENABLED", "true")
        
        try:
            result = start_scheduler()
            assert result is False
            assert is_scheduler_running() is False
        finally:
            stop_scheduler()

    def test_scheduled_refresh_started_when_enabled_and_real(self, monkeypatch):
        """Test scheduler starts when enabled and in real mode"""
        from app.scheduler.integration_scheduler import start_scheduler, stop_scheduler, is_scheduler_running
        
        monkeypatch.setenv("ODOO_PROVIDER_MODE", "real")
        monkeypatch.setenv("ODOO_SCHEDULED_REFRESH_ENABLED", "true")
        monkeypatch.setenv("ODOO_BASE_URL", "http://localhost:8069")
        monkeypatch.setenv("ODOO_DB", "odoo")
        monkeypatch.setenv("ODOO_USERNAME", "admin")
        monkeypatch.setenv("ODOO_API_KEY", "test-key")
        monkeypatch.setenv("ODOO_REFRESH_INTERVAL_INVENTORY", "900")
        monkeypatch.setenv("ODOO_REFRESH_INTERVAL_AUDIT", "1800")
        
        try:
            result = start_scheduler()
            assert result is True
            assert is_scheduler_running() is True
        finally:
            stop_scheduler()

    def test_scheduled_refresh_no_duplicate_start(self, monkeypatch):
        """Test scheduler does not start twice"""
        from app.scheduler.integration_scheduler import start_scheduler, stop_scheduler, is_scheduler_running
        
        monkeypatch.setenv("ODOO_PROVIDER_MODE", "real")
        monkeypatch.setenv("ODOO_SCHEDULED_REFRESH_ENABLED", "true")
        monkeypatch.setenv("ODOO_BASE_URL", "http://localhost:8069")
        monkeypatch.setenv("ODOO_DB", "odoo")
        monkeypatch.setenv("ODOO_USERNAME", "admin")
        monkeypatch.setenv("ODOO_API_KEY", "test-key")
        
        try:
            result1 = start_scheduler()
            result2 = start_scheduler()
            
            assert result1 is True
            assert result2 is True
            assert is_scheduler_running() is True
        finally:
            stop_scheduler()

    def test_inventory_refresh_job_scheduled(self, monkeypatch):
        """Test inventory refresh job is scheduled"""
        from app.scheduler.integration_scheduler import (
            start_scheduler, stop_scheduler, _scheduler
        )
        
        monkeypatch.setenv("ODOO_PROVIDER_MODE", "real")
        monkeypatch.setenv("ODOO_SCHEDULED_REFRESH_ENABLED", "true")
        monkeypatch.setenv("ODOO_BASE_URL", "http://localhost:8069")
        monkeypatch.setenv("ODOO_DB", "odoo")
        monkeypatch.setenv("ODOO_USERNAME", "admin")
        monkeypatch.setenv("ODOO_API_KEY", "test-key")
        monkeypatch.setenv("ODOO_REFRESH_INTERVAL_INVENTORY", "900")
        
        try:
            start_scheduler()
            
            job = _scheduler.get_job("refresh_inventory")
            assert job is not None
            assert job.name == "Inventory Refresh"
        finally:
            stop_scheduler()

    def test_audit_refresh_job_scheduled(self, monkeypatch):
        """Test audit refresh job is scheduled"""
        from app.scheduler.integration_scheduler import (
            start_scheduler, stop_scheduler, _scheduler
        )
        
        monkeypatch.setenv("ODOO_PROVIDER_MODE", "real")
        monkeypatch.setenv("ODOO_SCHEDULED_REFRESH_ENABLED", "true")
        monkeypatch.setenv("ODOO_BASE_URL", "http://localhost:8069")
        monkeypatch.setenv("ODOO_DB", "odoo")
        monkeypatch.setenv("ODOO_USERNAME", "admin")
        monkeypatch.setenv("ODOO_API_KEY", "test-key")
        monkeypatch.setenv("ODOO_REFRESH_INTERVAL_AUDIT", "1800")
        
        try:
            start_scheduler()
            
            job = _scheduler.get_job("refresh_audit")
            assert job is not None
            assert job.name == "Audit Refresh"
        finally:
            stop_scheduler()


class TestRefreshMethods:
    """Test refresh_inventory and refresh_audit methods"""

    def test_refresh_inventory_method(self, db_session):
        """Test refresh_inventory method"""
        from app.services.integration_service import IntegrationService
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        service = IntegrationService(db_session, odoo_provider=provider)
        
        result = service.refresh_inventory(trigger_type="scheduled")
        
        assert result["inventory_count"] == 2
        assert "successfully" in result["message"]

    def test_refresh_audit_method(self, db_session):
        """Test refresh_audit method"""
        from app.services.integration_service import IntegrationService
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        service = IntegrationService(db_session, odoo_provider=provider)
        
        result = service.refresh_audit(trigger_type="scheduled")
        
        assert result["audit_count"] == 2
        assert "successfully" in result["message"]

    def test_scheduled_refresh_records_sync_status(self, db_session):
        """Test scheduled refresh records trigger_type=scheduled"""
        from app.services.integration_service import IntegrationService
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        service = IntegrationService(db_session, odoo_provider=provider)
        
        service.refresh_inventory(trigger_type="scheduled")
        
        sync_status = service.get_latest_sync_status()
        assert sync_status is not None
        assert sync_status["trigger_type"] == "scheduled"
        assert sync_status["status"] == "success"

    def test_scheduled_refresh_records_failure(self, db_session):
        """Test scheduled refresh records failure status"""
        from unittest.mock import MagicMock
        from app.services.integration_service import IntegrationService
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        provider.get_inventory_list = MagicMock(side_effect=Exception("Connection failed"))
        service = IntegrationService(db_session, odoo_provider=provider)
        
        with pytest.raises(Exception, match="Connection failed"):
            service.refresh_inventory(trigger_type="scheduled")
        
        sync_status = service.get_latest_sync_status()
        assert sync_status is not None
        assert sync_status["status"] == "failed"
        assert "Connection failed" in sync_status["error_summary"]

    def test_manual_refresh_still_works(self, db_session):
        """Test manual refresh still works after adding scheduled refresh"""
        from app.services.integration_service import IntegrationService
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        service = IntegrationService(db_session, odoo_provider=provider)
        
        result = service.refresh_from_provider(trigger_type="manual")
        
        assert result["inventory_count"] == 2
        assert result["audit_count"] == 2
        assert result["exception_count"] == 2
        
        sync_status = service.get_latest_sync_status()
        assert sync_status["trigger_type"] == "manual"
