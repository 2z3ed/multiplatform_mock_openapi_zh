"""
Service-level tests for blacklist_customer
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.blacklist_customer import BlacklistCustomer
from shared_db.base import Base
from app.services.blacklist_customer_service import BlacklistCustomerService


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestBlacklistCustomerService:
    """Test blacklist_customer service"""

    def test_create_blacklist(self, db_session):
        """Test creating blacklist customer through service"""
        service = BlacklistCustomerService(db_session)
        result = service.create(
            customer_id=1,
            reason="Test reason",
            source="manual"
        )

        assert result is not None
        assert result["customer_id"] == 1
        assert result["reason"] == "Test reason"
        assert result["source"] == "manual"

    def test_create_with_invalid_source(self, db_session):
        """Test creating blacklist customer with invalid source returns None"""
        service = BlacklistCustomerService(db_session)
        result = service.create(
            customer_id=1,
            source="invalid_source"
        )

        assert result is None

    def test_create_duplicate_customer(self, db_session):
        """Test creating blacklist customer with duplicate customer_id returns None"""
        service = BlacklistCustomerService(db_session)
        service.create(customer_id=1)

        result = service.create(customer_id=1)
        assert result is None

    def test_get_by_id(self, db_session):
        """Test getting blacklist customer by id"""
        service = BlacklistCustomerService(db_session)
        created = service.create(customer_id=1)

        result = service.get_by_id(created["id"])
        assert result is not None
        assert result["id"] == created["id"]

    def test_get_by_customer_id(self, db_session):
        """Test getting blacklist customer by customer_id"""
        service = BlacklistCustomerService(db_session)
        service.create(customer_id=1)

        result = service.get_by_customer_id(1)
        assert result is not None
        assert result["customer_id"] == 1

    def test_list_all(self, db_session):
        """Test listing all blacklist customers"""
        service = BlacklistCustomerService(db_session)
        service.create(customer_id=1)
        service.create(customer_id=2)

        results = service.list_all()
        assert len(results) == 2

    def test_delete(self, db_session):
        """Test deleting blacklist customer"""
        service = BlacklistCustomerService(db_session)
        service.create(customer_id=1)

        success = service.delete(1)
        assert success is True

        result = service.get_by_customer_id(1)
        assert result is None

    def test_delete_non_existent(self, db_session):
        """Test deleting non-existent blacklist customer returns False"""
        service = BlacklistCustomerService(db_session)
        success = service.delete(9999)
        assert success is False
