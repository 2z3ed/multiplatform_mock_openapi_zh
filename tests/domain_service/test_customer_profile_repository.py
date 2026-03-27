"""
Repository-level tests for customer profile
"""

import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.customer_profile import CustomerProfile
from domain_models.models.customer import Customer
from shared_db.base import Base
from app.repositories.customer_profile_repository import CustomerProfileRepository


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


class TestCustomerProfileRepository:
    """Test customer profile repository"""

    def test_create_profile(self, db_session, setup_data):
        """Test creating profile in database"""
        repo = CustomerProfileRepository(db_session)
        profile = repo.create(
            customer_id=1,
            total_orders=10,
            total_spent=Decimal("1000.00"),
            avg_order_value=Decimal("100.00")
        )

        assert profile.id is not None
        assert profile.customer_id == 1
        assert profile.total_orders == 10
        assert profile.total_spent == Decimal("1000.00")
        assert profile.avg_order_value == Decimal("100.00")
        assert profile.created_at is not None

    def test_get_by_customer_id_exists(self, db_session, setup_data):
        """Test getting existing profile"""
        repo = CustomerProfileRepository(db_session)
        created = repo.create(
            customer_id=1,
            total_orders=5,
            total_spent=Decimal("500.00"),
            avg_order_value=Decimal("100.00")
        )

        result = repo.get_by_customer_id(1)
        assert result is not None
        assert result.id == created.id
        assert result.total_orders == 5

    def test_get_by_customer_id_not_exists(self, db_session):
        """Test getting non-existent profile returns None"""
        repo = CustomerProfileRepository(db_session)
        result = repo.get_by_customer_id(9999)
        assert result is None

    def test_update_profile(self, db_session, setup_data):
        """Test updating profile fields"""
        repo = CustomerProfileRepository(db_session)
        repo.create(
            customer_id=1,
            total_orders=5,
            total_spent=Decimal("500.00"),
            avg_order_value=Decimal("100.00")
        )

        result = repo.update(1, {"total_orders": 10, "total_spent": Decimal("1000.00")})
        assert result is not None
        assert result.total_orders == 10
        assert result.total_spent == Decimal("1000.00")

    def test_delete_exists(self, db_session, setup_data):
        """Test deleting existing profile returns True"""
        repo = CustomerProfileRepository(db_session)
        repo.create(
            customer_id=1,
            total_orders=5,
            total_spent=Decimal("500.00"),
            avg_order_value=Decimal("100.00")
        )

        result = repo.delete(1)
        assert result is True

        deleted = repo.get_by_customer_id(1)
        assert deleted is None

    def test_delete_not_exists(self, db_session):
        """Test deleting non-existent profile returns False"""
        repo = CustomerProfileRepository(db_session)
        result = repo.delete(9999)
        assert result is False
