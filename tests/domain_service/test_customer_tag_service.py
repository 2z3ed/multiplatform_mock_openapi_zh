"""
Service-level tests for customer tag
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.customer_tag import CustomerTag
from domain_models.models.customer import Customer
from domain_models.models.audit_log import AuditLog
from shared_db.base import Base
from app.services.tag_service import CustomerTagService


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def setup_data(db_session):
    customer = Customer(id=1, platform="jd", platform_customer_id="customer_001")
    db_session.add(customer)
    db_session.commit()
    return {"customer": customer}


class TestCustomerTagService:
    """Test customer tag service"""

    def test_create_tag_success(self, db_session, setup_data):
        """Test creating tag successfully"""
        service = CustomerTagService(db_session=db_session)
        result = service.create_tag(
            customer_id=1,
            tag_type="behavior",
            tag_value="high_value"
        )

        assert result is not None
        assert result["customer_id"] == 1
        assert result["tag_type"] == "behavior"
        assert result["tag_value"] == "high_value"
        assert result["source"] == "manual"

    def test_create_tag_invalid_tag_type(self, db_session, setup_data):
        """Test creating tag with invalid tag_type returns None"""
        service = CustomerTagService(db_session=db_session)
        result = service.create_tag(
            customer_id=1,
            tag_type="invalid_type",
            tag_value="some_value"
        )
        assert result is None

    def test_create_tag_invalid_source(self, db_session, setup_data):
        """Test creating tag with invalid source returns None"""
        service = CustomerTagService(db_session=db_session)
        result = service.create_tag(
            customer_id=1,
            tag_type="behavior",
            tag_value="some_value",
            source="rule"
        )
        assert result is None

    def test_create_tag_duplicate(self, db_session, setup_data):
        """Test creating duplicate tag returns None"""
        service = CustomerTagService(db_session=db_session)
        service.create_tag(
            customer_id=1,
            tag_type="preference",
            tag_value="electronics"
        )

        result = service.create_tag(
            customer_id=1,
            tag_type="preference",
            tag_value="electronics"
        )
        assert result is None

    def test_get_tag_exists(self, db_session, setup_data):
        """Test getting existing tag"""
        service = CustomerTagService(db_session=db_session)
        created = service.create_tag(
            customer_id=1,
            tag_type="segment",
            tag_value="vip"
        )

        result = service.get_tag(created["id"])
        assert result is not None
        assert result["id"] == created["id"]
        assert result["tag_value"] == "vip"

    def test_get_tag_not_exists(self, db_session):
        """Test getting non-existent tag returns None"""
        service = CustomerTagService(db_session=db_session)
        result = service.get_tag(9999)
        assert result is None

    def test_list_tags(self, db_session, setup_data):
        """Test listing tags by customer_id"""
        service = CustomerTagService(db_session=db_session)
        service.create_tag(customer_id=1, tag_type="behavior", tag_value="high_value")
        service.create_tag(customer_id=1, tag_type="preference", tag_value="electronics")
        service.create_tag(customer_id=2, tag_type="custom", tag_value="other")

        results = service.list_tags(1)
        assert len(results) == 2

    def test_delete_tag_exists(self, db_session, setup_data):
        """Test deleting existing tag returns True"""
        service = CustomerTagService(db_session=db_session)
        created = service.create_tag(customer_id=1, tag_type="behavior", tag_value="test")

        result = service.delete_tag(created["id"])
        assert result is True

        deleted = service.get_tag(created["id"])
        assert deleted is None

    def test_delete_tag_not_exists(self, db_session):
        """Test deleting non-existent tag returns False"""
        service = CustomerTagService(db_session=db_session)
        result = service.delete_tag(9999)
        assert result is False


class TestCustomerTagAuditLogs:
    """Test customer tag audit logging"""

    def test_create_tag_logs_audit(self, db_session, setup_data):
        """Test creating tag writes customer_tag_created audit"""
        service = CustomerTagService(db_session=db_session)
        result = service.create_tag(
            customer_id=1,
            tag_type="behavior",
            tag_value="high_value"
        )

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "customer_tag_created"
        ).all()
        
        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(result["id"])
        assert audit_logs[0].detail_json["tag_type"] == "behavior"
        assert audit_logs[0].detail_json["tag_value"] == "high_value"

    def test_create_tag_failure_does_not_log_audit(self, db_session, setup_data):
        """Test creating tag with invalid tag_type does not write audit"""
        service = CustomerTagService(db_session=db_session)
        service.create_tag(
            customer_id=1,
            tag_type="invalid_type",
            tag_value="some_value"
        )

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "customer_tag_created"
        ).all()
        
        assert len(audit_logs) == 0

    def test_delete_tag_logs_audit(self, db_session, setup_data):
        """Test deleting tag writes customer_tag_deleted audit"""
        service = CustomerTagService(db_session=db_session)
        created = service.create_tag(
            customer_id=1,
            tag_type="behavior",
            tag_value="test"
        )

        service.delete_tag(created["id"])

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "customer_tag_deleted"
        ).all()
        
        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(created["id"])
        assert audit_logs[0].detail_json["tag_type"] == "behavior"
        assert audit_logs[0].detail_json["tag_value"] == "test"

    def test_delete_nonexistent_tag_does_not_log_audit(self, db_session, setup_data):
        """Test deleting non-existent tag does not write audit"""
        service = CustomerTagService(db_session=db_session)
        service.delete_tag(9999)

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "customer_tag_deleted"
        ).all()
        
        assert len(audit_logs) == 0
