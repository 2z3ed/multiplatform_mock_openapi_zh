"""
API-level tests for integration endpoints
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models import (
    Customer, Conversation, Message, OrderSnapshot, ShipmentSnapshot,
    AfterSaleCase, KBDocument, KBChunk, AISuggestion, AuditLog, FollowUpTask,
    CustomerTag, CustomerProfile, Recommendation, QualityRule, QualityInspectionResult, QualityAlert,
    RiskCase, BlacklistCustomer,
    ERPInventorySnapshot, OrderAuditSnapshot, OrderExceptionSnapshot
)
from shared_db.base import Base
from app.main import app
from shared_db import get_db


TEST_DB_URL = "sqlite:///test_integration.db"


@pytest.fixture
def db_session():
    if os.path.exists("test_integration.db"):
        os.remove("test_integration.db")
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    if os.path.exists("test_integration.db"):
        os.remove("test_integration.db")


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestIntegrationAPI:
    """Test integration API endpoints"""

    def test_create_inventory_snapshot(self, client):
        """Test POST /api/integration/inventory"""
        response = client.post("/api/integration/inventory", json={
            "sku_code": "SKU001",
            "warehouse_code": "WH-BJ",
            "available_qty": 100,
            "reserved_qty": 10,
            "status": "normal"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["sku_code"] == "SKU001"
        assert data["available_qty"] == 100

    def test_create_inventory_snapshot_invalid_status(self, client):
        """Test POST /api/integration/inventory with invalid status"""
        response = client.post("/api/integration/inventory", json={
            "sku_code": "SKU001",
            "warehouse_code": "WH-BJ",
            "available_qty": 100,
            "status": "invalid"
        })

        assert response.status_code == 422

    def test_list_inventory(self, client):
        """Test GET /api/integration/inventory"""
        client.post("/api/integration/inventory", json={
            "sku_code": "SKU001",
            "warehouse_code": "WH-BJ",
            "available_qty": 100
        })
        client.post("/api/integration/inventory", json={
            "sku_code": "SKU002",
            "warehouse_code": "WH-SH",
            "available_qty": 50
        })

        response = client.get("/api/integration/inventory")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_inventory_by_sku_code(self, client):
        """Test GET /api/integration/inventory?sku_code=xxx"""
        client.post("/api/integration/inventory", json={
            "sku_code": "SKU001",
            "warehouse_code": "WH-BJ",
            "available_qty": 100
        })
        client.post("/api/integration/inventory", json={
            "sku_code": "SKU002",
            "warehouse_code": "WH-SH",
            "available_qty": 50
        })

        response = client.get("/api/integration/inventory?sku_code=SKU001")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["sku_code"] == "SKU001"

    def test_get_inventory_by_sku_code(self, client):
        """Test GET /api/integration/inventory/{sku_code}"""
        client.post("/api/integration/inventory", json={
            "sku_code": "SKU001",
            "warehouse_code": "WH-BJ",
            "available_qty": 100
        })

        response = client.get("/api/integration/inventory/SKU001")
        assert response.status_code == 200
        data = response.json()
        assert data["sku_code"] == "SKU001"

    def test_get_inventory_not_found(self, client):
        """Test GET /api/integration/inventory/{sku_code} not found"""
        response = client.get("/api/integration/inventory/SKU999")
        assert response.status_code == 404

    def test_create_order_audit_snapshot(self, client):
        """Test POST /api/integration/order-audits"""
        response = client.post("/api/integration/order-audits", json={
            "order_id": "ORD001",
            "platform": "taobao",
            "audit_status": "approved"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["order_id"] == "ORD001"
        assert data["audit_status"] == "approved"

    def test_list_order_audits(self, client):
        """Test GET /api/integration/order-audits"""
        client.post("/api/integration/order-audits", json={
            "order_id": "ORD001",
            "platform": "taobao",
            "audit_status": "approved"
        })
        client.post("/api/integration/order-audits", json={
            "order_id": "ORD002",
            "platform": "jd",
            "audit_status": "pending"
        })

        response = client.get("/api/integration/order-audits")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_get_order_audit_by_order_id(self, client):
        """Test GET /api/integration/order-audits/{order_id}"""
        client.post("/api/integration/order-audits", json={
            "order_id": "ORD001",
            "platform": "taobao",
            "audit_status": "approved"
        })

        response = client.get("/api/integration/order-audits/ORD001")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "ORD001"

    def test_get_order_audit_not_found(self, client):
        """Test GET /api/integration/order-audits/{order_id} not found"""
        response = client.get("/api/integration/order-audits/ORD999")
        assert response.status_code == 404

    def test_create_order_exception_snapshot(self, client):
        """Test POST /api/integration/order-exceptions"""
        response = client.post("/api/integration/order-exceptions", json={
            "order_id": "ORD001",
            "platform": "taobao",
            "exception_type": "delay",
            "exception_status": "open"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["order_id"] == "ORD001"
        assert data["exception_type"] == "delay"

    def test_list_order_exceptions(self, client):
        """Test GET /api/integration/order-exceptions"""
        client.post("/api/integration/order-exceptions", json={
            "order_id": "ORD001",
            "platform": "taobao",
            "exception_type": "delay",
            "exception_status": "open"
        })
        client.post("/api/integration/order-exceptions", json={
            "order_id": "ORD002",
            "platform": "jd",
            "exception_type": "stockout",
            "exception_status": "processing"
        })

        response = client.get("/api/integration/order-exceptions")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_order_exceptions_by_type(self, client):
        """Test GET /api/integration/order-exceptions?exception_type=xxx"""
        client.post("/api/integration/order-exceptions", json={
            "order_id": "ORD001",
            "platform": "taobao",
            "exception_type": "delay",
            "exception_status": "open"
        })
        client.post("/api/integration/order-exceptions", json={
            "order_id": "ORD002",
            "platform": "jd",
            "exception_type": "stockout",
            "exception_status": "processing"
        })

        response = client.get("/api/integration/order-exceptions?exception_type=delay")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["exception_type"] == "delay"

    def test_get_order_exception_by_order_id(self, client):
        """Test GET /api/integration/order-exceptions/{order_id}"""
        client.post("/api/integration/order-exceptions", json={
            "order_id": "ORD001",
            "platform": "taobao",
            "exception_type": "delay",
            "exception_status": "open"
        })

        response = client.get("/api/integration/order-exceptions/ORD001")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "ORD001"

    def test_get_order_exception_not_found(self, client):
        """Test GET /api/integration/order-exceptions/{order_id} not found"""
        response = client.get("/api/integration/order-exceptions/ORD999")
        assert response.status_code == 404

    def test_explain_status_inventory(self, client):
        """Test POST /api/integration/explain-status for inventory"""
        client.post("/api/integration/inventory", json={
            "sku_code": "SKU001",
            "warehouse_code": "WH-BJ",
            "available_qty": 100,
            "status": "normal"
        })

        response = client.post("/api/integration/explain-status", json={
            "type": "inventory",
            "sku_code": "SKU001"
        })

        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert "suggestion" in data

    def test_explain_status_audit(self, client):
        """Test POST /api/integration/explain-status for audit"""
        client.post("/api/integration/order-audits", json={
            "order_id": "ORD001",
            "platform": "taobao",
            "audit_status": "approved"
        })

        response = client.post("/api/integration/explain-status", json={
            "type": "audit",
            "order_id": "ORD001"
        })

        assert response.status_code == 200
        data = response.json()
        assert "已通过审核" in data["explanation"]

    def test_explain_status_exception(self, client):
        """Test POST /api/integration/explain-status for exception"""
        client.post("/api/integration/order-exceptions", json={
            "order_id": "ORD001",
            "platform": "taobao",
            "exception_type": "delay",
            "exception_status": "open"
        })

        response = client.post("/api/integration/explain-status", json={
            "type": "exception",
            "order_id": "ORD001"
        })

        assert response.status_code == 200
        data = response.json()
        assert "物流延误" in data["explanation"]
