"""
API-level tests for analytics endpoints
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.recommendation import Recommendation
from domain_models.models.follow_up_task import FollowUpTask
from domain_models.models.operation_campaign import OperationCampaign
from domain_models.models.customer import Customer
from domain_models.models.conversation import Conversation
from shared_db.base import Base
from app.main import app
from app.api.analytics import get_analytics_service
from app.services.analytics_service import AnalyticsService


TEST_DB_URL = "sqlite:///test_analytics.db"


@pytest.fixture
def db_session():
    import os
    if os.path.exists("test_analytics.db"):
        os.remove("test_analytics.db")
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    customer = Customer(id=1, platform="test", platform_customer_id="test_001", display_name="Test")
    session.add(customer)
    conversation = Conversation(id=1, customer_id=1, platform="test", status="active")
    session.add(conversation)
    session.commit()
    
    yield session
    session.close()
    if os.path.exists("test_analytics.db"):
        os.remove("test_analytics.db")


@pytest.fixture
def test_client(db_session):
    def override_get_analytics_service():
        return AnalyticsService(db_session=db_session)

    app.dependency_overrides[get_analytics_service] = override_get_analytics_service

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestAnalyticsAPI:
    """Test analytics API endpoints"""

    def test_summarize_success(self, test_client, db_session):
        """Test POST /api/analytics/summarize creates summary"""
        response = test_client.post(
            "/api/analytics/summarize",
            json={"stat_date": "2026-03-28"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["stat_date"] == "2026-03-28"
        assert data["recommendation_created_count"] == 0

    def test_summarize_empty_data_returns_zeros(self, test_client):
        """Test POST /api/analytics/summarize with no data returns zeros"""
        response = test_client.post(
            "/api/analytics/summarize",
            json={"stat_date": "2026-03-28"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["recommendation_created_count"] == 0
        assert data["recommendation_accepted_count"] == 0
        assert data["followup_executed_count"] == 0
        assert data["followup_closed_count"] == 0
        assert data["operation_campaign_completed_count"] == 0

    def test_summarize_with_data(self, test_client, db_session):
        """Test POST /api/analytics/summarize with recommendation data"""
        rec = Recommendation(
            conversation_id=1,
            customer_id=1,
            product_id="P1",
            product_name="Product 1",
            status="pending",
            created_at=datetime(2026, 3, 28, 10, 0, 0)
        )
        db_session.add(rec)
        db_session.commit()

        response = test_client.post(
            "/api/analytics/summarize",
            json={"stat_date": "2026-03-28"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["recommendation_created_count"] == 1

    def test_summarize_invalid_date_format(self, test_client):
        """Test POST /api/analytics/summarize with invalid date format returns 400"""
        response = test_client.post(
            "/api/analytics/summarize",
            json={"stat_date": "28-03-2026"}
        )

        assert response.status_code == 400

    def test_get_summary_success(self, test_client):
        """Test GET /api/analytics/summary/{stat_date} returns summary"""
        test_client.post(
            "/api/analytics/summarize",
            json={"stat_date": "2026-03-28"}
        )

        response = test_client.get("/api/analytics/summary/2026-03-28")

        assert response.status_code == 200
        data = response.json()
        assert data["stat_date"] == "2026-03-28"

    def test_get_summary_not_exists(self, test_client):
        """Test GET /api/analytics/summary/{stat_date} returns 404 when not exists"""
        response = test_client.get("/api/analytics/summary/2026-03-28")

        assert response.status_code == 404

    def test_get_summary_invalid_date_format(self, test_client):
        """Test GET /api/analytics/summary/{stat_date} with invalid format returns 400"""
        response = test_client.get("/api/analytics/summary/invalid-date")

        assert response.status_code == 400

    def test_list_summaries(self, test_client):
        """Test GET /api/analytics/summaries returns list"""
        test_client.post(
            "/api/analytics/summarize",
            json={"stat_date": "2026-03-28"}
        )
        test_client.post(
            "/api/analytics/summarize",
            json={"stat_date": "2026-03-29"}
        )

        response = test_client.get(
            "/api/analytics/summaries?start_date=2026-03-28&end_date=2026-03-30"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_summaries_empty_range(self, test_client):
        """Test GET /api/analytics/summaries returns empty list"""
        test_client.post(
            "/api/analytics/summarize",
            json={"stat_date": "2026-03-28"}
        )

        response = test_client.get(
            "/api/analytics/summaries?start_date=2026-04-01&end_date=2026-04-30"
        )

        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_summaries_missing_params(self, test_client):
        """Test GET /api/analytics/summaries returns 422 when params missing"""
        response = test_client.get("/api/analytics/summaries")

        assert response.status_code == 422

    def test_list_summaries_invalid_date_format(self, test_client):
        """Test GET /api/analytics/summaries returns 400 when date format invalid"""
        response = test_client.get(
            "/api/analytics/summaries?start_date=invalid&end_date=2026-03-30"
        )

        assert response.status_code == 400

    def test_list_summaries_start_greater_than_end(self, test_client):
        """Test GET /api/analytics/summaries returns 400 when start_date > end_date"""
        response = test_client.get(
            "/api/analytics/summaries?start_date=2026-03-30&end_date=2026-03-28"
        )

        assert response.status_code == 400
