from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from domain_models.models.analytics_summary import AnalyticsSummary


class AnalyticsSummaryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        stat_date: date,
        recommendation_created_count: int = 0,
        recommendation_accepted_count: int = 0,
        followup_executed_count: int = 0,
        followup_closed_count: int = 0,
        operation_campaign_completed_count: int = 0,
        extra_json: Optional[dict] = None,
    ) -> AnalyticsSummary:
        summary = AnalyticsSummary(
            stat_date=stat_date,
            recommendation_created_count=recommendation_created_count,
            recommendation_accepted_count=recommendation_accepted_count,
            followup_executed_count=followup_executed_count,
            followup_closed_count=followup_closed_count,
            operation_campaign_completed_count=operation_campaign_completed_count,
            extra_json=extra_json,
        )
        self.db.add(summary)
        self.db.commit()
        self.db.refresh(summary)
        return summary

    def get_by_stat_date(self, stat_date: date) -> Optional[AnalyticsSummary]:
        return (
            self.db.query(AnalyticsSummary)
            .filter(AnalyticsSummary.stat_date == stat_date)
            .first()
        )

    def list_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[AnalyticsSummary]:
        return (
            self.db.query(AnalyticsSummary)
            .filter(
                AnalyticsSummary.stat_date >= start_date,
                AnalyticsSummary.stat_date <= end_date,
            )
            .order_by(AnalyticsSummary.stat_date.asc())
            .all()
        )

    def upsert_by_stat_date(
        self,
        stat_date: date,
        recommendation_created_count: int = 0,
        recommendation_accepted_count: int = 0,
        followup_executed_count: int = 0,
        followup_closed_count: int = 0,
        operation_campaign_completed_count: int = 0,
        extra_json: Optional[dict] = None,
    ) -> AnalyticsSummary:
        existing = self.get_by_stat_date(stat_date)
        if existing:
            existing.recommendation_created_count = recommendation_created_count
            existing.recommendation_accepted_count = recommendation_accepted_count
            existing.followup_executed_count = followup_executed_count
            existing.followup_closed_count = followup_closed_count
            existing.operation_campaign_completed_count = operation_campaign_completed_count
            existing.extra_json = extra_json
            self.db.commit()
            self.db.refresh(existing)
            return existing
        return self.create(
            stat_date=stat_date,
            recommendation_created_count=recommendation_created_count,
            recommendation_accepted_count=recommendation_accepted_count,
            followup_executed_count=followup_executed_count,
            followup_closed_count=followup_closed_count,
            operation_campaign_completed_count=operation_campaign_completed_count,
            extra_json=extra_json,
        )
