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
