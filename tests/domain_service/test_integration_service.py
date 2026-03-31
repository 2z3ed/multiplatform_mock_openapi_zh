"""
Service-level tests for integration_service
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared_db.base import Base
from app.services.integration_service import IntegrationService
from app.repositories.erp_inventory_snapshot_repository import ERPInventorySnapshotRepository
from app.repositories.order_audit_snapshot_repository import OrderAuditSnapshotRepository
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


class TestIntegrationService:
    """Test integration service"""

    def test_create_inventory_snapshot(self, db_session):
        """Test creating inventory snapshot"""
        service = IntegrationService(db_session)
        result = service.create_inventory_snapshot(
            sku_code="SKU001",
            warehouse_code="WH-BJ",
            available_qty=100,
            reserved_qty=10,
            status="normal"
        )

        assert result["id"] is not None
        assert result["sku_code"] == "SKU001"
        assert result["available_qty"] == 100

    def test_create_inventory_snapshot_invalid_status(self, db_session):
        """Test creating inventory snapshot with invalid status"""
        service = IntegrationService(db_session)
        with pytest.raises(ValueError, match="Invalid status"):
            service.create_inventory_snapshot(
                sku_code="SKU001",
                warehouse_code="WH-BJ",
                available_qty=100,
                status="invalid_status"
            )

    def test_get_inventory_by_sku_code(self, db_session):
        """Test getting inventory by sku_code"""
        service = IntegrationService(db_session)
        service.create_inventory_snapshot(
            sku_code="SKU001",
            warehouse_code="WH-BJ",
            available_qty=100
        )

        result = service.get_inventory_by_sku_code("SKU001")
        assert result is not None
        assert result["sku_code"] == "SKU001"

    def test_list_inventory(self, db_session):
        """Test listing inventory snapshots"""
        service = IntegrationService(db_session)
        service.create_inventory_snapshot(sku_code="SKU001", warehouse_code="WH-BJ", available_qty=100)
        service.create_inventory_snapshot(sku_code="SKU002", warehouse_code="WH-SH", available_qty=50)

        results = service.list_inventory()
        assert len(results) == 2

    def test_list_inventory_by_sku_code(self, db_session):
        """Test listing inventory by sku_code"""
        service = IntegrationService(db_session)
        service.create_inventory_snapshot(sku_code="SKU001", warehouse_code="WH-BJ", available_qty=100)
        service.create_inventory_snapshot(sku_code="SKU001", warehouse_code="WH-SH", available_qty=50)
        service.create_inventory_snapshot(sku_code="SKU002", warehouse_code="WH-GZ", available_qty=200)

        results = service.list_inventory(sku_code="SKU001")
        assert len(results) == 2

    def test_create_order_audit_snapshot(self, db_session):
        """Test creating order audit snapshot"""
        service = IntegrationService(db_session)
        result = service.create_order_audit_snapshot(
            order_id="ORD001",
            platform="taobao",
            audit_status="approved"
        )

        assert result["id"] is not None
        assert result["order_id"] == "ORD001"
        assert result["audit_status"] == "approved"

    def test_create_order_audit_snapshot_invalid_status(self, db_session):
        """Test creating audit snapshot with invalid status"""
        service = IntegrationService(db_session)
        with pytest.raises(ValueError, match="Invalid audit_status"):
            service.create_order_audit_snapshot(
                order_id="ORD001",
                platform="taobao",
                audit_status="invalid_status"
            )

    def test_get_order_audit_by_order_id(self, db_session):
        """Test getting audit by order_id"""
        service = IntegrationService(db_session)
        service.create_order_audit_snapshot(
            order_id="ORD001",
            platform="taobao",
            audit_status="approved"
        )

        result = service.get_order_audit_by_order_id("ORD001")
        assert result is not None
        assert result["order_id"] == "ORD001"

    def test_list_order_audits(self, db_session):
        """Test listing audit snapshots"""
        service = IntegrationService(db_session)
        service.create_order_audit_snapshot(order_id="ORD001", platform="taobao", audit_status="approved")
        service.create_order_audit_snapshot(order_id="ORD002", platform="jd", audit_status="pending")

        results = service.list_order_audits()
        assert len(results) == 2

    def test_create_order_exception_snapshot(self, db_session):
        """Test creating order exception snapshot"""
        service = IntegrationService(db_session)
        result = service.create_order_exception_snapshot(
            order_id="ORD001",
            platform="taobao",
            exception_type="delay",
            exception_status="open"
        )

        assert result["id"] is not None
        assert result["order_id"] == "ORD001"
        assert result["exception_type"] == "delay"

    def test_create_order_exception_snapshot_invalid_type(self, db_session):
        """Test creating exception snapshot with invalid type"""
        service = IntegrationService(db_session)
        with pytest.raises(ValueError, match="Invalid exception_type"):
            service.create_order_exception_snapshot(
                order_id="ORD001",
                platform="taobao",
                exception_type="invalid_type",
                exception_status="open"
            )

    def test_get_order_exception_by_order_id(self, db_session):
        """Test getting exception by order_id"""
        service = IntegrationService(db_session)
        service.create_order_exception_snapshot(
            order_id="ORD001",
            platform="taobao",
            exception_type="delay",
            exception_status="open"
        )

        result = service.get_order_exception_by_order_id("ORD001")
        assert result is not None
        assert result["order_id"] == "ORD001"

    def test_list_order_exceptions(self, db_session):
        """Test listing exception snapshots"""
        service = IntegrationService(db_session)
        service.create_order_exception_snapshot(order_id="ORD001", platform="taobao", exception_type="delay", exception_status="open")
        service.create_order_exception_snapshot(order_id="ORD002", platform="jd", exception_type="stockout", exception_status="processing")

        results = service.list_order_exceptions()
        assert len(results) == 2

    def test_explain_status_inventory_normal(self, db_session):
        """Test explaining inventory status - normal"""
        service = IntegrationService(db_session)
        service.create_inventory_snapshot(
            sku_code="SKU001",
            warehouse_code="WH-BJ",
            available_qty=100,
            status="normal"
        )

        result = service.explain_status(type="inventory", sku_code="SKU001")
        assert "库存充足" in result["explanation"]
        assert "发货" in result["suggestion"]

    def test_explain_status_inventory_out_of_stock(self, db_session):
        """Test explaining inventory status - out_of_stock"""
        service = IntegrationService(db_session)
        service.create_inventory_snapshot(
            sku_code="SKU002",
            warehouse_code="WH-BJ",
            available_qty=0,
            status="out_of_stock"
        )

        result = service.explain_status(type="inventory", sku_code="SKU002")
        assert "缺货" in result["explanation"]

    def test_explain_status_inventory_not_found(self, db_session):
        """Test explaining inventory status - not found"""
        service = IntegrationService(db_session)

        result = service.explain_status(type="inventory", sku_code="SKU999")
        assert "未找到" in result["explanation"]

    def test_explain_status_audit_approved(self, db_session):
        """Test explaining audit status - approved"""
        service = IntegrationService(db_session)
        service.create_order_audit_snapshot(
            order_id="ORD001",
            platform="taobao",
            audit_status="approved"
        )

        result = service.explain_status(type="audit", order_id="ORD001")
        assert "已通过审核" in result["explanation"]

    def test_explain_status_audit_rejected(self, db_session):
        """Test explaining audit status - rejected"""
        service = IntegrationService(db_session)
        service.create_order_audit_snapshot(
            order_id="ORD002",
            platform="taobao",
            audit_status="rejected",
            audit_reason="地址信息不完整"
        )

        result = service.explain_status(type="audit", order_id="ORD002")
        assert "审核未通过" in result["explanation"]
        assert "地址信息不完整" in result["explanation"]

    def test_explain_status_exception_delay(self, db_session):
        """Test explaining exception status - delay"""
        service = IntegrationService(db_session)
        service.create_order_exception_snapshot(
            order_id="ORD001",
            platform="taobao",
            exception_type="delay",
            exception_status="open"
        )

        result = service.explain_status(type="exception", order_id="ORD001")
        assert "物流延误" in result["explanation"]
        assert "open" in result["explanation"]

    def test_explain_status_missing_sku_code(self, db_session):
        """Test explaining status with missing sku_code"""
        service = IntegrationService(db_session)
        with pytest.raises(ValueError, match="sku_code is required"):
            service.explain_status(type="inventory")

    def test_explain_status_missing_order_id(self, db_session):
        """Test explaining status with missing order_id"""
        service = IntegrationService(db_session)
        with pytest.raises(ValueError, match="order_id is required"):
            service.explain_status(type="audit")

    def test_explain_status_invalid_type(self, db_session):
        """Test explaining status with invalid type"""
        service = IntegrationService(db_session)
        with pytest.raises(ValueError, match="Invalid type"):
            service.explain_status(type="invalid")


class TestIntegrationServiceWithOdooProvider:
    """Test integration service with Odoo provider"""

    def test_refresh_from_provider_without_provider(self, db_session):
        """Test refresh without provider injected"""
        service = IntegrationService(db_session)
        result = service.refresh_from_provider()
        assert result["inventory_count"] == 0
        assert result["audit_count"] == 0
        assert result["exception_count"] == 0
        assert "No Odoo provider configured" in result["message"]

    def test_refresh_inventory_from_odoo_provider(self, db_session):
        """Test refreshing inventory from Odoo provider"""
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        service = IntegrationService(db_session, odoo_provider=provider)
        
        result = service.refresh_from_provider()
        assert result["inventory_count"] == 2
        assert "successfully" in result["message"]
        
        inventory_list = service.list_inventory()
        assert len(inventory_list) >= 2
        
        sku_codes = [inv["sku_code"] for inv in inventory_list]
        assert "ODOO-SKU-001" in sku_codes
        assert "ODOO-SKU-002" in sku_codes

    def test_refresh_order_audit_from_odoo_provider(self, db_session):
        """Test refreshing order audit from Odoo provider"""
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        service = IntegrationService(db_session, odoo_provider=provider)
        
        result = service.refresh_from_provider()
        assert result["audit_count"] == 2
        
        audit_list = service.list_order_audits()
        assert len(audit_list) >= 2
        
        order_ids = [audit["order_id"] for audit in audit_list]
        assert "ODOO-ORD-001" in order_ids
        assert "ODOO-ORD-002" in order_ids

    def test_refresh_order_exception_from_odoo_provider(self, db_session):
        """Test refreshing order exception from Odoo provider"""
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        service = IntegrationService(db_session, odoo_provider=provider)
        
        result = service.refresh_from_provider()
        assert result["exception_count"] == 2
        
        exception_list = service.list_order_exceptions()
        assert len(exception_list) >= 2
        
        order_ids = [exc["order_id"] for exc in exception_list]
        assert "ODOO-ORD-003" in order_ids
        assert "ODOO-ORD-004" in order_ids

    def test_list_after_refresh(self, db_session):
        """Test that list methods return data after refresh"""
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        service = IntegrationService(db_session, odoo_provider=provider)
        
        assert len(service.list_inventory()) == 0
        assert len(service.list_order_audits()) == 0
        assert len(service.list_order_exceptions()) == 0
        
        service.refresh_from_provider()
        
        assert len(service.list_inventory()) == 2
        assert len(service.list_order_audits()) == 2
        assert len(service.list_order_exceptions()) == 2

    def test_explain_status_after_refresh(self, db_session):
        """Test that explain_status works with refreshed data"""
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        service = IntegrationService(db_session, odoo_provider=provider)
        service.refresh_from_provider()
        
        result = service.explain_status(type="inventory", sku_code="ODOO-SKU-001")
        assert "库存充足" in result["explanation"]
        
        result = service.explain_status(type="audit", order_id="ODOO-ORD-001")
        assert "已通过审核" in result["explanation"]
        
        result = service.explain_status(type="exception", order_id="ODOO-ORD-003")
        assert "物流延误" in result["explanation"]


class TestOdooRealProvider:
    """Test Odoo real provider with mocked client"""

    def test_odoo_client_can_be_created(self):
        """Test OdooClient can be instantiated"""
        from providers.odoo.real.client import OdooClient
        
        client = OdooClient(
            base_url="http://localhost:8069",
            db="odoo",
            username="admin",
            api_key="test-key",
        )
        assert client is not None

    def test_odoo_real_provider_can_be_created(self):
        """Test OdooRealProvider can be instantiated"""
        from providers.odoo.real.client import OdooClient
        from providers.odoo.real.provider import OdooRealProvider
        
        client = OdooClient(
            base_url="http://localhost:8069",
            db="odoo",
            username="admin",
            api_key="test-key",
        )
        provider = OdooRealProvider(client)
        assert provider is not None

    def test_odoo_real_provider_get_inventory_list_with_mock(self, db_session):
        """Test get_inventory_list returns standardized structure with mocked client"""
        from unittest.mock import MagicMock
        from providers.odoo.real.client import OdooClient
        from providers.odoo.real.provider import OdooRealProvider
        
        client = OdooClient(
            base_url="http://localhost:8069",
            db="odoo",
            username="admin",
            api_key="test-key",
        )
        client.search_read = MagicMock(return_value=[
            {
                "id": 1,
                "product_id": [101, "Product A"],
                "location_id": [1, "WH-BJ"],
                "quantity": 100,
                "reserved_quantity": 10,
            },
            {
                "id": 2,
                "product_id": [102, "Product B"],
                "location_id": [2, "WH-SH"],
                "quantity": 5,
                "reserved_quantity": 2,
            },
        ])
        
        provider = OdooRealProvider(client)
        result = provider.get_inventory_list()
        
        assert len(result) == 2
        assert result[0]["sku_code"] == "Product A"
        assert result[0]["available_qty"] == 90
        assert result[0]["status"] == "normal"
        assert "source_json" in result[0]
        assert result[0]["source_json"]["odoo_model"] == "stock.quant"

    def test_odoo_real_provider_get_order_audit_list_with_mock(self, db_session):
        """Test get_order_audit_list returns standardized structure with mocked client"""
        from unittest.mock import MagicMock
        from providers.odoo.real.client import OdooClient
        from providers.odoo.real.provider import OdooRealProvider
        
        client = OdooClient(
            base_url="http://localhost:8069",
            db="odoo",
            username="admin",
            api_key="test-key",
        )
        client.search_read = MagicMock(return_value=[
            {
                "id": 1,
                "name": "SO001",
                "state": "sale",
                "note": None,
            },
            {
                "id": 2,
                "name": "SO002",
                "state": "draft",
                "note": None,
            },
        ])
        
        provider = OdooRealProvider(client)
        result = provider.get_order_audit_list()
        
        assert len(result) == 2
        assert result[0]["order_id"] == "SO001"
        assert result[0]["audit_status"] == "approved"
        assert "source_json" in result[0]
        assert result[0]["source_json"]["odoo_model"] == "sale.order"

    def test_odoo_real_provider_get_order_exception_list_with_mock(self, db_session):
        """Test get_order_exception_list returns standardized structure with mocked client"""
        from unittest.mock import MagicMock
        from providers.odoo.real.client import OdooClient
        from providers.odoo.real.provider import OdooRealProvider
        
        client = OdooClient(
            base_url="http://localhost:8069",
            db="odoo",
            username="admin",
            api_key="test-key",
        )
        client.search_read = MagicMock(return_value=[
            {
                "id": 1,
                "name": "SO001",
                "state": "sale",
                "note": "Shipping delay reported",
            },
            {
                "id": 2,
                "name": "SO002",
                "state": "sale",
                "note": "Out of stock issue",
            },
        ])
        
        provider = OdooRealProvider(client)
        result = provider.get_order_exception_list()
        
        assert len(result) == 2
        assert result[0]["order_id"] == "SO001"
        assert result[0]["exception_type"] == "delay"
        assert "detail_json" in result[0]
        assert result[0]["detail_json"]["odoo_model"] == "sale.order"

    def test_integration_service_with_real_provider_stub(self, db_session):
        """Test integration_service with real provider stub"""
        from unittest.mock import MagicMock
        from providers.odoo.real.client import OdooClient
        from providers.odoo.real.provider import OdooRealProvider
        
        client = OdooClient(
            base_url="http://localhost:8069",
            db="odoo",
            username="admin",
            api_key="test-key",
        )
        client.search_read = MagicMock(return_value=[
            {
                "id": 1,
                "product_id": [101, "Real-Product-A"],
                "location_id": [1, "Real-WH-BJ"],
                "quantity": 50,
                "reserved_quantity": 5,
            },
        ])
        
        provider = OdooRealProvider(client)
        service = IntegrationService(db_session, odoo_provider=provider)
        
        result = service.refresh_from_provider()
        assert result["inventory_count"] == 1
        
        inventory_list = service.list_inventory()
        assert len(inventory_list) == 1
        assert inventory_list[0]["sku_code"] == "Real-Product-A"


class TestProviderFactory:
    """Test provider factory"""

    def test_provider_factory_returns_mock_by_default(self, monkeypatch):
        """Test provider_factory returns mock provider by default"""
        monkeypatch.delenv("ODOO_PROVIDER_MODE", raising=False)
        
        from providers.odoo.provider_factory import get_odoo_provider
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = get_odoo_provider()
        assert isinstance(provider, OdooMockProvider)

    def test_provider_factory_returns_mock_when_configured(self, monkeypatch):
        """Test provider_factory returns mock provider when configured"""
        monkeypatch.setenv("ODOO_PROVIDER_MODE", "mock")
        
        from providers.odoo.provider_factory import get_odoo_provider
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = get_odoo_provider()
        assert isinstance(provider, OdooMockProvider)

    def test_provider_factory_returns_real_when_configured(self, monkeypatch):
        """Test provider_factory returns real provider when configured"""
        monkeypatch.setenv("ODOO_PROVIDER_MODE", "real")
        monkeypatch.setenv("ODOO_BASE_URL", "http://localhost:8069")
        monkeypatch.setenv("ODOO_DB", "odoo")
        monkeypatch.setenv("ODOO_USERNAME", "admin")
        monkeypatch.setenv("ODOO_API_KEY", "test-key")
        
        from providers.odoo.provider_factory import get_odoo_provider
        from providers.odoo.real.provider import OdooRealProvider
        
        provider = get_odoo_provider()
        assert isinstance(provider, OdooRealProvider)

    def test_provider_factory_raises_when_real_but_missing_config(self, monkeypatch):
        """Test provider_factory raises error when real mode but missing config"""
        monkeypatch.setenv("ODOO_PROVIDER_MODE", "real")
        monkeypatch.delenv("ODOO_BASE_URL", raising=False)
        monkeypatch.delenv("ODOO_DB", raising=False)
        monkeypatch.delenv("ODOO_USERNAME", raising=False)
        monkeypatch.delenv("ODOO_API_KEY", raising=False)
        
        from providers.odoo.provider_factory import get_odoo_provider, ProviderConfigError
        
        with pytest.raises(ProviderConfigError, match="missing required config"):
            get_odoo_provider()

    def test_provider_factory_raises_on_invalid_mode(self, monkeypatch):
        """Test provider_factory raises error on invalid mode"""
        monkeypatch.setenv("ODOO_PROVIDER_MODE", "invalid")
        
        from providers.odoo.provider_factory import get_odoo_provider, ProviderConfigError
        
        with pytest.raises(ProviderConfigError, match="Invalid ODOO_PROVIDER_MODE"):
            get_odoo_provider()


class TestSyncStatusRecording:
    """Test sync status recording"""

    def test_refresh_records_sync_status(self, db_session):
        """Test refresh records sync status"""
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        service = IntegrationService(db_session, odoo_provider=provider)
        
        result = service.refresh_from_provider()
        assert result["inventory_count"] == 2
        
        sync_status = service.get_latest_sync_status()
        assert sync_status is not None
        assert sync_status["status"] == "success"
        assert sync_status["inventory_count"] == 2
        assert sync_status["audit_count"] == 2
        assert sync_status["exception_count"] == 2
        assert sync_status["provider_mode"] == "mock"
        assert sync_status["trigger_type"] == "manual"

    def test_refresh_records_error_on_failure(self, db_session):
        """Test refresh records error on failure"""
        from unittest.mock import MagicMock
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        provider.get_inventory_list = MagicMock(side_effect=Exception("Connection failed"))
        service = IntegrationService(db_session, odoo_provider=provider)
        
        with pytest.raises(Exception, match="Connection failed"):
            service.refresh_from_provider()
        
        sync_status = service.get_latest_sync_status()
        assert sync_status is not None
        assert sync_status["status"] == "failed"
        assert "Connection failed" in sync_status["error_summary"]

    def test_refresh_without_provider_records_failed_status(self, db_session):
        """Test refresh without provider records failed status"""
        service = IntegrationService(db_session)
        
        result = service.refresh_from_provider()
        assert result["inventory_count"] == 0
        
        sync_status = service.get_latest_sync_status()
        assert sync_status is not None
        assert sync_status["status"] == "failed"
        assert "No Odoo provider configured" in sync_status["error_summary"]

    def test_get_latest_sync_status_returns_none_when_empty(self, db_session):
        """Test get_latest_sync_status returns None when no sync has occurred"""
        service = IntegrationService(db_session)
        
        sync_status = service.get_latest_sync_status()
        assert sync_status is None

    def test_refresh_with_trigger_type(self, db_session):
        """Test refresh with custom trigger type"""
        from providers.odoo.mock.provider import OdooMockProvider
        
        provider = OdooMockProvider()
        service = IntegrationService(db_session, odoo_provider=provider)
        
        result = service.refresh_from_provider(trigger_type="api")
        assert result["inventory_count"] == 2
        
        sync_status = service.get_latest_sync_status()
        assert sync_status["trigger_type"] == "api"
