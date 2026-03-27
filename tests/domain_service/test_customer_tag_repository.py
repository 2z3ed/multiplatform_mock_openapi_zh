"""
Repository-level tests for customer tag
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.customer_tag import CustomerTag
from domain_models.models.customer import Customer
from shared_db.base import Base
from app.repositories.customer_tag_repository import CustomerTagRepository


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


class TestCustomerTagRepository:
    """Test customer tag repository"""

    def test_create_tag(self, db_session, setup_data):
        """Test creating tag in database"""
        repo = CustomerTagRepository(db_session)
        tag = repo.create(
            customer_id=1,
            tag_type="behavior",
            tag_value="high_value",
            source="manual"
        )

        assert tag.id is not None
        assert tag.customer_id == 1
        assert tag.tag_type == "behavior"
        assert tag.tag_value == "high_value"
        assert tag.source == "manual"
        assert tag.created_at is not None

    def test_create_tag_defaults(self, db_session, setup_data):
        """Test default values"""
        repo = CustomerTagRepository(db_session)
        tag = repo.create(
            customer_id=1,
            tag_type="preference",
            tag_value="electronics"
        )

        assert tag.source == "manual"
        assert tag.extra_json is None

    def test_get_by_id_exists(self, db_session, setup_data):
        """Test getting existing tag"""
        repo = CustomerTagRepository(db_session)
        created = repo.create(
            customer_id=1,
            tag_type="segment",
            tag_value="vip"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id
        assert result.tag_value == "vip"

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent tag returns None"""
        repo = CustomerTagRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_list_by_customer_id(self, db_session, setup_data):
        """Test listing tags by customer_id"""
        repo = CustomerTagRepository(db_session)
        repo.create(customer_id=1, tag_type="behavior", tag_value="high_value")
        repo.create(customer_id=1, tag_type="preference", tag_value="electronics")
        repo.create(customer_id=2, tag_type="custom", tag_value="other")

        results = repo.list_by_customer_id(1)
        assert len(results) == 2

    def test_delete_exists(self, db_session, setup_data):
        """Test deleting existing tag returns True"""
        repo = CustomerTagRepository(db_session)
        created = repo.create(customer_id=1, tag_type="behavior", tag_value="test")

        result = repo.delete(created.id)
        assert result is True

        deleted = repo.get_by_id(created.id)
        assert deleted is None

    def test_delete_not_exists(self, db_session):
        """Test deleting non-existent tag returns False"""
        repo = CustomerTagRepository(db_session)
        result = repo.delete(9999)
        assert result is False
