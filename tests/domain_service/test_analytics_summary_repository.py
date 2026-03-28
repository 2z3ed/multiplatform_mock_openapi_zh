"""
Repository-level tests for analytics summary
"""

import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain_models.models.analytics_summary import AnalyticsSummary
from shared_db.base import Base
from app.repositories.analytics_summary_repository import AnalyticsSummaryRepository


TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


class TestAnalyticsSummaryRepository:
    """Test analytics summary repository"""

    def test_create_analytics_summary(self, db_session):
        """Test creating analytics summary"""
        repo = AnalyticsSummaryRepository(db=db_session)
        result = repo.create(
            stat_date=date(2026, 3, 28),
            recommendation_created_count=10,
            recommendation_accepted_count=5,
            followup_executed_count=3,
            followup_closed_count=2,
            operation_campaign_completed_count=1,
        )

        assert result is not None
        assert result.stat_date == date(2026, 3, 28)
        assert result.recommendation_created_count == 10
        assert result.recommendation_accepted_count == 5
        assert result.followup_executed_count == 3
        assert result.followup_closed_count == 2
        assert result.operation_campaign_completed_count == 1

    def test_create_defaults_to_zero(self, db_session):
        """Test creating analytics summary with default values"""
        repo = AnalyticsSummaryRepository(db=db_session)
        result = repo.create(stat_date=date(2026, 3, 28))

        assert result.recommendation_created_count == 0
        assert result.recommendation_accepted_count == 0
        assert result.followup_executed_count == 0
        assert result.followup_closed_count == 0
        assert result.operation_campaign_completed_count == 0

    def test_extra_json_nullable(self, db_session):
        """Test creating analytics summary with null extra_json"""
        repo = AnalyticsSummaryRepository(db=db_session)
        result = repo.create(stat_date=date(2026, 3, 28))

        assert result.extra_json is None

    def test_get_by_stat_date_exists(self, db_session):
        """Test getting analytics summary by stat_date when exists"""
        repo = AnalyticsSummaryRepository(db=db_session)
        repo.create(
            stat_date=date(2026, 3, 28),
            recommendation_created_count=10,
        )

        result = repo.get_by_stat_date(date(2026, 3, 28))

        assert result is not None
        assert result.stat_date == date(2026, 3, 28)
        assert result.recommendation_created_count == 10

    def test_get_by_stat_date_not_exists(self, db_session):
        """Test getting analytics summary by stat_date when not exists"""
        repo = AnalyticsSummaryRepository(db=db_session)
        result = repo.get_by_stat_date(date(2026, 3, 28))

        assert result is None

    def test_list_by_date_range(self, db_session):
        """Test listing analytics summaries by date range"""
        repo = AnalyticsSummaryRepository(db=db_session)
        repo.create(stat_date=date(2026, 3, 28), recommendation_created_count=10)
        repo.create(stat_date=date(2026, 3, 29), recommendation_created_count=20)
        repo.create(stat_date=date(2026, 3, 30), recommendation_created_count=30)

        results = repo.list_by_date_range(date(2026, 3, 28), date(2026, 3, 30))

        assert len(results) == 3
        assert results[0].stat_date == date(2026, 3, 28)
        assert results[1].stat_date == date(2026, 3, 29)
        assert results[2].stat_date == date(2026, 3, 30)

    def test_list_by_date_range_empty(self, db_session):
        """Test listing analytics summaries when no data in range"""
        repo = AnalyticsSummaryRepository(db=db_session)
        repo.create(stat_date=date(2026, 3, 28), recommendation_created_count=10)

        results = repo.list_by_date_range(date(2026, 4, 1), date(2026, 4, 30))

        assert len(results) == 0

    def test_list_by_date_range_sorted_asc(self, db_session):
        """Test listing analytics summaries sorted by stat_date asc"""
        repo = AnalyticsSummaryRepository(db=db_session)
        repo.create(stat_date=date(2026, 3, 30), recommendation_created_count=30)
        repo.create(stat_date=date(2026, 3, 28), recommendation_created_count=10)
        repo.create(stat_date=date(2026, 3, 29), recommendation_created_count=20)

        results = repo.list_by_date_range(date(2026, 3, 28), date(2026, 3, 30))

        assert results[0].stat_date == date(2026, 3, 28)
        assert results[1].stat_date == date(2026, 3, 29)
        assert results[2].stat_date == date(2026, 3, 30)

    def test_upsert_creates_new(self, db_session):
        """Test upsert creates new record when not exists"""
        repo = AnalyticsSummaryRepository(db=db_session)
        result = repo.upsert_by_stat_date(
            stat_date=date(2026, 3, 28),
            recommendation_created_count=10,
        )

        assert result is not None
        assert result.stat_date == date(2026, 3, 28)
        assert result.recommendation_created_count == 10

    def test_upsert_updates_existing(self, db_session):
        """Test upsert updates existing record"""
        repo = AnalyticsSummaryRepository(db=db_session)
        repo.create(stat_date=date(2026, 3, 28), recommendation_created_count=10)

        result = repo.upsert_by_stat_date(
            stat_date=date(2026, 3, 28),
            recommendation_created_count=20,
        )

        assert result.recommendation_created_count == 20

    def test_stat_date_unique(self, db_session):
        """Test stat_date unique constraint"""
        repo = AnalyticsSummaryRepository(db=db_session)
        repo.create(stat_date=date(2026, 3, 28), recommendation_created_count=10)

        from sqlalchemy.exc import IntegrityError

        try:
            repo.create(stat_date=date(2026, 3, 28), recommendation_created_count=20)
            assert False, "Should have raised IntegrityError"
        except IntegrityError:
            pass
