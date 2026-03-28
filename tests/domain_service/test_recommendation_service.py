"""
Service-level tests for recommendation
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from domain_models.models.audit_log import AuditLog
from shared_db.base import Base
from app.services.recommendation_service import RecommendationService


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


class TestRecommendationService:
    """Test recommendation service"""

    def test_create_recommendation_default_status_pending(self, db_session, setup_data):
        """Test creating recommendation defaults to pending status"""
        service = RecommendationService(db_session=db_session)
        result = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        assert result is not None
        assert result["status"] == "pending"

    def test_create_recommendation_accepts_null_reason(self, db_session, setup_data):
        """Test creating recommendation with null reason"""
        service = RecommendationService(db_session=db_session)
        result = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product",
            reason=None
        )

        assert result is not None
        assert result["reason"] is None

    def test_create_recommendation_accepts_null_suggested_copy(self, db_session, setup_data):
        """Test creating recommendation with null suggested_copy"""
        service = RecommendationService(db_session=db_session)
        result = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product",
            suggested_copy=None
        )

        assert result is not None
        assert result["suggested_copy"] is None

    def test_get_recommendation_by_id_returns_correct_object(self, db_session, setup_data):
        """Test getting recommendation by id returns correct object"""
        service = RecommendationService(db_session=db_session)
        created = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        result = service.get_recommendation_by_id(created["id"])
        assert result is not None
        assert result["id"] == created["id"]
        assert result["product_id"] == "PROD001"

    def test_get_recommendation_by_id_not_exists(self, db_session):
        """Test getting non-existent recommendation returns None"""
        service = RecommendationService(db_session=db_session)
        result = service.get_recommendation_by_id(9999)
        assert result is None

    def test_list_recommendations_by_conversation_returns_correct_list(self, db_session, setup_data):
        """Test listing recommendations by conversation_id"""
        service = RecommendationService(db_session=db_session)
        
        service.create_recommendation(
            conversation_id=1, customer_id=1, product_id="PROD001", product_name="Product 1"
        )
        service.create_recommendation(
            conversation_id=1, customer_id=1, product_id="PROD002", product_name="Product 2"
        )
        service.create_recommendation(
            conversation_id=2, customer_id=1, product_id="PROD003", product_name="Product 3"
        )

        results = service.list_recommendations_by_conversation(1)
        assert len(results) == 2
        product_ids = [r["product_id"] for r in results]
        assert "PROD001" in product_ids
        assert "PROD002" in product_ids
        assert "PROD003" not in product_ids

    def test_list_recommendations_by_conversation_empty(self, db_session, setup_data):
        """Test listing recommendations for conversation with no recommendations"""
        service = RecommendationService(db_session=db_session)
        results = service.list_recommendations_by_conversation(1)
        assert len(results) == 0

    def test_accept_recommendation_pending_to_accepted_success(self, db_session, setup_data):
        """Test accepting recommendation from pending to accepted succeeds"""
        service = RecommendationService(db_session=db_session)
        created = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        result = service.accept_recommendation(created["id"])
        assert result is not None
        assert result["status"] == "accepted"

    def test_accept_recommendation_not_exists_returns_failure(self, db_session):
        """Test accepting non-existent recommendation returns None"""
        service = RecommendationService(db_session=db_session)
        result = service.accept_recommendation(9999)
        assert result is None

    def test_accept_recommendation_rejects_when_not_pending(self, db_session, setup_data):
        """Test accepting recommendation that is not pending returns None"""
        service = RecommendationService(db_session=db_session)
        created = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )
        service.accept_recommendation(created["id"])

        result = service.accept_recommendation(created["id"])
        assert result is None

    def test_reject_recommendation_pending_to_rejected_success(self, db_session, setup_data):
        """Test rejecting recommendation from pending to rejected succeeds"""
        service = RecommendationService(db_session=db_session)
        created = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        result = service.reject_recommendation(created["id"])
        assert result is not None
        assert result["status"] == "rejected"

    def test_reject_recommendation_not_exists_returns_failure(self, db_session):
        """Test rejecting non-existent recommendation returns None"""
        service = RecommendationService(db_session=db_session)
        result = service.reject_recommendation(9999)
        assert result is None

    def test_reject_recommendation_rejects_when_not_pending(self, db_session, setup_data):
        """Test rejecting recommendation that is not pending returns None"""
        service = RecommendationService(db_session=db_session)
        created = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )
        service.reject_recommendation(created["id"])

        result = service.reject_recommendation(created["id"])
        assert result is None


class TestRecommendationAuditLogs:
    """Test recommendation audit logging"""

    def test_create_recommendation_logs_audit(self, db_session, setup_data):
        """Test creating recommendation writes recommendation_created audit"""
        service = RecommendationService(db_session=db_session)
        result = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "recommendation_created"
        ).all()
        
        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(result["id"])
        assert audit_logs[0].detail_json["product_id"] == "PROD001"

    def test_accept_recommendation_logs_audit(self, db_session, setup_data):
        """Test accepting recommendation writes recommendation_accepted audit"""
        service = RecommendationService(db_session=db_session)
        created = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        service.accept_recommendation(created["id"])

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "recommendation_accepted"
        ).all()
        
        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(created["id"])
        assert audit_logs[0].detail_json["status"] == "accepted"

    def test_reject_recommendation_logs_audit(self, db_session, setup_data):
        """Test rejecting recommendation writes recommendation_rejected audit"""
        service = RecommendationService(db_session=db_session)
        created = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        service.reject_recommendation(created["id"])

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "recommendation_rejected"
        ).all()
        
        assert len(audit_logs) == 1
        assert audit_logs[0].target_id == str(created["id"])
        assert audit_logs[0].detail_json["status"] == "rejected"

    def test_accept_failure_does_not_log_audit(self, db_session, setup_data):
        """Test accepting non-existent recommendation does not write audit"""
        service = RecommendationService(db_session=db_session)
        service.accept_recommendation(9999)

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "recommendation_accepted"
        ).all()
        
        assert len(audit_logs) == 0

    def test_accept_not_pending_does_not_log_audit(self, db_session, setup_data):
        """Test accepting non-pending recommendation does not write audit"""
        service = RecommendationService(db_session=db_session)
        created = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        service.accept_recommendation(created["id"])
        service.accept_recommendation(created["id"])

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "recommendation_accepted"
        ).all()
        
        assert len(audit_logs) == 1

    def test_reject_failure_does_not_log_audit(self, db_session, setup_data):
        """Test rejecting non-existent recommendation does not write audit"""
        service = RecommendationService(db_session=db_session)
        service.reject_recommendation(9999)

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "recommendation_rejected"
        ).all()
        
        assert len(audit_logs) == 0

    def test_reject_not_pending_does_not_log_audit(self, db_session, setup_data):
        """Test rejecting non-pending recommendation does not write audit"""
        service = RecommendationService(db_session=db_session)
        created = service.create_recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="PROD001",
            product_name="Test Product"
        )

        service.reject_recommendation(created["id"])
        service.reject_recommendation(created["id"])

        audit_logs = db_session.query(AuditLog).filter(
            AuditLog.action == "recommendation_rejected"
        ).all()
        
        assert len(audit_logs) == 1
