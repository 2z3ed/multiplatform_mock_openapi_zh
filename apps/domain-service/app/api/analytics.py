from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.schemas.analytics import (
    AnalyticsSummarizeRequest,
    AnalyticsSummaryResponse
)
from app.services.analytics_service import AnalyticsService
from shared_db import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db_session=db)


def parse_date(date_str: str, param_name: str) -> date:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {param_name} format. Expected YYYY-MM-DD"
        )


@router.post("/summarize", response_model=AnalyticsSummaryResponse)
def summarize(
    req: AnalyticsSummarizeRequest,
    service: AnalyticsService = Depends(get_analytics_service)
):
    stat_date = parse_date(req.stat_date, "stat_date")
    result = service.summarize_by_date(stat_date)
    return result


@router.get("/summary/{stat_date}", response_model=AnalyticsSummaryResponse)
def get_summary(
    stat_date: str,
    service: AnalyticsService = Depends(get_analytics_service)
):
    parsed_date = parse_date(stat_date, "stat_date")
    result = service.get_summary_by_date(parsed_date)
    if result is None:
        raise HTTPException(status_code=404, detail="Summary not found")
    return result


@router.get("/summaries", response_model=list[AnalyticsSummaryResponse])
def list_summaries(
    start_date: str = Query(..., description="Start date YYYY-MM-DD"),
    end_date: str = Query(..., description="End date YYYY-MM-DD"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    parsed_start = parse_date(start_date, "start_date")
    parsed_end = parse_date(end_date, "end_date")

    if parsed_start > parsed_end:
        raise HTTPException(
            status_code=400,
            detail="start_date must be less than or equal to end_date"
        )

    results = service.list_summaries(parsed_start, parsed_end)
    return results
