"""
Service-level tests for customer profile
"""

import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.customer_profile import CustomerProfile
from domain_models.models.customer import Customer
from shared_db.base import Base
from app.services.profile_service import CustomerProfileService


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


class TestCustomerProfileService:
    """Test customer profile service"""

    def test_create_profile_success(self, db_session, setup_data):
        """Test creating profile successfully"""
        service = CustomerProfileService(db_session=db_session)
        result = service.create_profile(
            customer_id=1,
            total_orders=10,
            total_spent=Decimal("1000.00"),
            avg_order_value=Decimal("100.00")
        )

        assert result is not None
        assert result["customer_id"] == 1
        assert result["total_orders"] == 10
        assert result["total_spent"] == "1000.00"
        assert result["avg_order_value"] == "100.00"

    def test_create_profile_duplicate(self, db_session, setup_data):
        """Test creating duplicate profile returns None"""
        service = CustomerProfileService(db_session=db_session)
        service.create_profile(
            customer_id=1,
            total_orders=10,
            total_spent=Decimal("1000.00"),
            avg_order_value=Decimal("100.00")
        )

        result = service.create_profile(
            customer_id=1,
            total_orders=5,
            total_spent=Decimal("500.00"),
            avg_order_value=Decimal("100.00")
        )
        assert result is None

    def test_create_profile_invalid_total_orders(self, db_session, setup_data):
        """Test creating profile with negative total_orders returns None"""
        service = CustomerProfileService(db_session=db_session)
        result = service.create_profile(
            customer_id=1,
            total_orders=-1,
            total_spent=Decimal("1000.00"),
            avg_order_value=Decimal("100.00")
        )
        assert result is None

    def test_create_profile_invalid_total_spent(self, db_session, setup_data):
        """Test creating profile with negative total_spent returns None"""
        service = CustomerProfileService(db_session=db_session)
        result = service.create_profile(
            customer_id=1,
            total_orders=10,
            total_spent=Decimal("-100.00"),
            avg_order_value=Decimal("100.00")
        )
        assert result is None

    def test_create_profile_invalid_avg_order_value(self, db_session, setup_data):
        """Test creating profile with negative avg_order_value returns None"""
        service = CustomerProfileService(db_session=db_session)
        result = service.create_profile(
            customer_id=1,
            total_orders=10,
            total_spent=Decimal("1000.00"),
            avg_order_value=Decimal("-10.00")
        )
        assert result is None

    def test_get_profile_exists(self, db_session, setup_data):
        """Test getting existing profile"""
        service = CustomerProfileService(db_session=db_session)
        created = service.create_profile(
            customer_id=1,
            total_orders=10,
            total_spent=Decimal("1000.00"),
            avg_order_value=Decimal("100.00")
        )

        result = service.get_profile(1)
        assert result is not None
        assert result["id"] == created["id"]
        assert result["total_orders"] == 10

    def test_get_profile_not_exists(self, db_session):
        """Test getting non-existent profile returns None"""
        service = CustomerProfileService(db_session=db_session)
        result = service.get_profile(9999)
        assert result is None

    def test_update_profile_success(self, db_session, setup_data):
        """Test updating profile successfully"""
        service = CustomerProfileService(db_session=db_session)
        service.create_profile(
            customer_id=1,
            total_orders=5,
            total_spent=Decimal("500.00"),
            avg_order_value=Decimal("100.00")
        )

        result = service.update_profile(1, {"total_orders": 10, "total_spent": Decimal("1000.00")})
        assert result is not None
        assert result["total_orders"] == 10
        assert result["total_spent"] == "1000.00"

    def test_update_profile_empty_updates(self, db_session, setup_data):
        """Test updating with empty updates returns None"""
        service = CustomerProfileService(db_session=db_session)
        service.create_profile(
            customer_id=1,
            total_orders=5,
            total_spent=Decimal("500.00"),
            avg_order_value=Decimal("100.00")
        )

        result = service.update_profile(1, {})
        assert result is None

    def test_update_profile_invalid_values(self, db_session, setup_data):
        """Test updating with invalid values returns None"""
        service = CustomerProfileService(db_session=db_session)
        service.create_profile(
            customer_id=1,
            total_orders=5,
            total_spent=Decimal("500.00"),
            avg_order_value=Decimal("100.00")
        )

        result = service.update_profile(1, {"total_orders": -1})
        assert result is None

    def test_delete_profile_exists(self, db_session, setup_data):
        """Test deleting existing profile returns True"""
        service = CustomerProfileService(db_session=db_session)
        service.create_profile(
            customer_id=1,
            total_orders=5,
            total_spent=Decimal("500.00"),
            avg_order_value=Decimal("100.00")
        )

        result = service.delete_profile(1)
        assert result is True

        deleted = service.get_profile(1)
        assert deleted is None

    def test_delete_profile_not_exists(self, db_session):
        """Test deleting non-existent profile returns False"""
        service = CustomerProfileService(db_session=db_session)
        result = service.delete_profile(9999)
        assert result is False
