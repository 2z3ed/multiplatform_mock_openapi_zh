"""
Repository-level tests for blacklist_customer
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.blacklist_customer import BlacklistCustomer
from shared_db.base import Base
from app.repositories.blacklist_customer_repository import BlacklistCustomerRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestBlacklistCustomerRepository:
    """Test blacklist_customer repository"""

    def test_create_blacklist(self, db_session):
        """Test creating blacklist customer in database"""
        repo = BlacklistCustomerRepository(db_session)
        blacklist = repo.create(
            customer_id=1,
            reason="Test reason",
            source="manual"
        )

        assert blacklist.id is not None
        assert blacklist.customer_id == 1
        assert blacklist.reason == "Test reason"
        assert blacklist.source == "manual"

    def test_create_with_minimal_fields(self, db_session):
        """Test creating blacklist customer with minimal fields"""
        repo = BlacklistCustomerRepository(db_session)
        blacklist = repo.create(customer_id=1)

        assert blacklist.id is not None
        assert blacklist.source == "manual"
        assert blacklist.reason is None

    def test_get_by_id_exists(self, db_session):
        """Test getting existing blacklist customer by id"""
        repo = BlacklistCustomerRepository(db_session)
        created = repo.create(customer_id=1)

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent blacklist customer returns None"""
        repo = BlacklistCustomerRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_get_by_customer_id_exists(self, db_session):
        """Test getting existing blacklist customer by customer_id"""
        repo = BlacklistCustomerRepository(db_session)
        repo.create(customer_id=1)

        result = repo.get_by_customer_id(1)
        assert result is not None
        assert result.customer_id == 1

    def test_get_by_customer_id_not_exists(self, db_session):
        """Test getting non-existent blacklist customer by customer_id returns None"""
        repo = BlacklistCustomerRepository(db_session)
        result = repo.get_by_customer_id(9999)
        assert result is None

    def test_list_all(self, db_session):
        """Test listing all blacklist customers"""
        repo = BlacklistCustomerRepository(db_session)
        repo.create(customer_id=1, reason="Customer 1")
        repo.create(customer_id=2, reason="Customer 2")

        results = repo.list_all()
        assert len(results) == 2

    def test_unique_customer_id(self, db_session):
        """Test that customer_id must be unique"""
        repo = BlacklistCustomerRepository(db_session)
        repo.create(customer_id=1)

        with pytest.raises(Exception):
            repo.create(customer_id=1)

    def test_delete_by_customer_id(self, db_session):
        """Test deleting blacklist customer by customer_id"""
        repo = BlacklistCustomerRepository(db_session)
        repo.create(customer_id=1)

        success = repo.delete_by_customer_id(1)
        assert success is True

        result = repo.get_by_customer_id(1)
        assert result is None

    def test_delete_non_existent(self, db_session):
        """Test deleting non-existent blacklist customer returns False"""
        repo = BlacklistCustomerRepository(db_session)
        success = repo.delete_by_customer_id(9999)
        assert success is False

    def test_exists_true(self, db_session):
        """Test exists returns True when customer is blacklisted"""
        repo = BlacklistCustomerRepository(db_session)
        repo.create(customer_id=1)

        exists = repo.exists(1)
        assert exists is True

    def test_exists_false(self, db_session):
        """Test exists returns False when customer is not blacklisted"""
        repo = BlacklistCustomerRepository(db_session)
        exists = repo.exists(9999)
        assert exists is False
