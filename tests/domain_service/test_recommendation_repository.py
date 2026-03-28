"""
Repository-level tests for recommendation
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.recommendation import Recommendation
from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from shared_db.base import Base
from app.repositories.recommendation_repository import RecommendationRepository


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
    conversation = Conversation(id=1, platform="jd", customer_id=1, status="open")
    db_session.add(conversation)
    db_session.commit()
    return {"customer": customer, "conversation": conversation}


class TestRecommendationRepository:
    """Test recommendation repository"""

    def test_create_recommendation(self, db_session, setup_data):
        """Test creating recommendation in database"""
        repo = RecommendationRepository(db_session)
        recommendation = repo.create(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product",
            reason="Recommended based on your purchase history",
            suggested_copy="You might also like this product!"
        )

        assert recommendation.id is not None
        assert recommendation.conversation_id == 1
        assert recommendation.customer_id == 1
        assert recommendation.product_id == "PROD001"
        assert recommendation.product_name == "Test Product"
        assert recommendation.status == "pending"
        assert recommendation.created_at is not None

    def test_create_with_reason_and_suggested_copy_null(self, db_session, setup_data):
        """Test creating recommendation with null reason and suggested_copy"""
        repo = RecommendationRepository(db_session)
        recommendation = repo.create(
            conversation_id=1,
            customer_id=1,
            product_id="PROD002",
            product_name="Another Product"
        )

        assert recommendation.id is not None
        assert recommendation.reason is None
        assert recommendation.suggested_copy is None

    def test_create_with_extra_json(self, db_session, setup_data):
        """Test creating recommendation with extra_json"""
        repo = RecommendationRepository(db_session)
        extra_data = {"source": "ai_recommendation", "score": 0.95}
        recommendation = repo.create(
            conversation_id=1,
            customer_id=1,
            product_id="PROD003",
            product_name="Product With Extra",
            extra_json=extra_data
        )

        assert recommendation.extra_json == extra_data

    def test_get_by_id_exists(self, db_session, setup_data):
        """Test getting existing recommendation by id"""
        repo = RecommendationRepository(db_session)
        created = repo.create(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        result = repo.get_by_id(created.id)
        assert result is not None
        assert result.id == created.id
        assert result.product_id == "PROD001"

    def test_get_by_id_not_exists(self, db_session):
        """Test getting non-existent recommendation returns None"""
        repo = RecommendationRepository(db_session)
        result = repo.get_by_id(9999)
        assert result is None

    def test_list_by_conversation(self, db_session, setup_data):
        """Test listing recommendations by conversation_id"""
        repo = RecommendationRepository(db_session)
        
        repo.create(conversation_id=1, customer_id=1, product_id="PROD001", product_name="Product 1")
        repo.create(conversation_id=1, customer_id=1, product_id="PROD002", product_name="Product 2")
        repo.create(conversation_id=2, customer_id=1, product_id="PROD003", product_name="Product 3")

        results = repo.list_by_conversation(1)
        assert len(results) == 2
        product_ids = [r.product_id for r in results]
        assert "PROD001" in product_ids
        assert "PROD002" in product_ids
        assert "PROD003" not in product_ids

    def test_list_by_conversation_empty(self, db_session, setup_data):
        """Test listing recommendations for conversation with no recommendations"""
        repo = RecommendationRepository(db_session)
        results = repo.list_by_conversation(1)
        assert len(results) == 0

    def test_update_status_pending_to_accepted(self, db_session, setup_data):
        """Test updating status from pending to accepted"""
        repo = RecommendationRepository(db_session)
        recommendation = repo.create(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        result = repo.update_status(recommendation.id, "accepted")
        assert result is not None
        assert result.status == "accepted"

    def test_update_status_pending_to_rejected(self, db_session, setup_data):
        """Test updating status from pending to rejected"""
        repo = RecommendationRepository(db_session)
        recommendation = repo.create(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        result = repo.update_status(recommendation.id, "rejected")
        assert result is not None
        assert result.status == "rejected"

    def test_update_status_invalid_status(self, db_session, setup_data):
        """Test updating status with invalid status value returns None"""
        repo = RecommendationRepository(db_session)
        recommendation = repo.create(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        result = repo.update_status(recommendation.id, "invalid_status")
        assert result is None

    def test_update_status_nonexistent_id(self, db_session):
        """Test updating status for non-existent recommendation returns None"""
        repo = RecommendationRepository(db_session)
        result = repo.update_status(9999, "accepted")
        assert result is None

    def test_conversation_id_filter_correct(self, db_session, setup_data):
        """Test that conversation_id foreign key is correctly stored"""
        repo = RecommendationRepository(db_session)
        
        repo.create(conversation_id=1, customer_id=1, product_id="PROD001", product_name="Product 1")
        repo.create(conversation_id=1, customer_id=1, product_id="PROD002", product_name="Product 2")
        
        results = repo.list_by_conversation(1)
        assert all(r.conversation_id == 1 for r in results)

    def test_customer_id_foreign_key_writes(self, db_session, setup_data):
        """Test customer_id foreign key field is correctly written"""
        repo = RecommendationRepository(db_session)
        recommendation = repo.create(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        assert recommendation.customer_id == 1
