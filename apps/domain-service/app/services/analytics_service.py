from datetime import date, datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from domain_models.models.recommendation import Recommendation
from domain_models.models.follow_up_task import FollowUpTask
from domain_models.models.operation_campaign import OperationCampaign
from domain_models.models.analytics_summary import AnalyticsSummary
from app.repositories.analytics_summary_repository import AnalyticsSummaryRepository
from app.services.audit_service import AuditService


class AnalyticsService:
    def __init__(self, db_session: Session):
        self._db_session = db_session
        self._repo = AnalyticsSummaryRepository(db_session)
        self._audit_service = AuditService(db_session)

    def _to_dict(self, summary: AnalyticsSummary) -> dict:
        return {
            "id": summary.id,
            "stat_date": summary.stat_date.isoformat() if summary.stat_date else None,
            "recommendation_created_count": summary.recommendation_created_count,
            "recommendation_accepted_count": summary.recommendation_accepted_count,
            "followup_executed_count": summary.followup_executed_count,
            "followup_closed_count": summary.followup_closed_count,
            "operation_campaign_completed_count": summary.operation_campaign_completed_count,
            "extra_json": summary.extra_json,
            "created_at": summary.created_at.isoformat() if summary.created_at else None,
            "updated_at": summary.updated_at.isoformat() if summary.updated_at else None,
        }

    def summarize_by_date(self, stat_date: date) -> dict:
        start_datetime = datetime.combine(stat_date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=1)

        recommendation_created = (
            self._db_session.query(func.count(Recommendation.id))
            .filter(
                and_(
                    Recommendation.created_at >= start_datetime,
                    Recommendation.created_at < end_datetime
                )
            )
            .scalar() or 0
        )

        recommendation_accepted = (
            self._db_session.query(func.count(Recommendation.id))
            .filter(
                and_(
                    Recommendation.status == "accepted",
                    Recommendation.updated_at >= start_datetime,
                    Recommendation.updated_at < end_datetime
                )
            )
            .scalar() or 0
        )

        followup_executed = (
            self._db_session.query(func.count(FollowUpTask.id))
            .filter(
                and_(
                    FollowUpTask.status == "completed",
                    FollowUpTask.completed_at >= start_datetime,
                    FollowUpTask.completed_at < end_datetime
                )
            )
            .scalar() or 0
        )

        followup_closed = (
            self._db_session.query(func.count(FollowUpTask.id))
            .filter(
                and_(
                    FollowUpTask.status == "closed",
                    FollowUpTask.completed_at >= start_datetime,
                    FollowUpTask.completed_at < end_datetime
                )
            )
            .scalar() or 0
        )

        operation_campaign_completed = (
            self._db_session.query(func.count(OperationCampaign.id))
            .filter(
                and_(
                    OperationCampaign.status == "completed",
                    OperationCampaign.updated_at >= start_datetime,
                    OperationCampaign.updated_at < end_datetime
                )
            )
            .scalar() or 0
        )

        result = self._repo.upsert_by_stat_date(
            stat_date=stat_date,
            recommendation_created_count=recommendation_created,
            recommendation_accepted_count=recommendation_accepted,
            followup_executed_count=followup_executed,
            followup_closed_count=followup_closed,
            operation_campaign_completed_count=operation_campaign_completed,
        )

        self._audit_service.analytics_summary_generated(
            stat_date=stat_date.isoformat(),
            recommendation_created_count=recommendation_created,
            recommendation_accepted_count=recommendation_accepted,
            followup_executed_count=followup_executed,
            followup_closed_count=followup_closed,
            operation_campaign_completed_count=operation_campaign_completed,
        )

        return self._to_dict(result)

    def get_summary_by_date(self, stat_date: date) -> Optional[dict]:
        summary = self._repo.get_by_stat_date(stat_date)
        if summary is None:
            return None
        return self._to_dict(summary)

    def list_summaries(self, start_date: date, end_date: date) -> list[dict]:
        summaries = self._repo.list_by_date_range(start_date, end_date)
        return [self._to_dict(s) for s in summaries]
