from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.recommendation import RecommendationCreateRequest, RecommendationResponse
from app.services.recommendation_service import RecommendationService
from shared_db import get_db

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])

conversation_router = APIRouter(tags=["recommendations"])


def get_recommendation_service(db: Session = Depends(get_db)) -> RecommendationService:
    return RecommendationService(db_session=db)


@router.post("", response_model=RecommendationResponse, status_code=201)
def create_recommendation(
    req: RecommendationCreateRequest,
    service: RecommendationService = Depends(get_recommendation_service)
):
    result = service.create_recommendation(
        conversation_id=req.conversation_id,
        customer_id=req.customer_id,
        product_id=req.product_id,
        product_name=req.product_name,
        reason=req.reason,
        suggested_copy=req.suggested_copy,
        extra_json=req.extra_json
    )
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to create recommendation")
    return result


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
def get_recommendation(
    recommendation_id: int,
    service: RecommendationService = Depends(get_recommendation_service)
):
    result = service.get_recommendation_by_id(recommendation_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return result


@conversation_router.get("/api/conversations/{conversation_id}/recommendations", response_model=list[RecommendationResponse])
def list_recommendations_by_conversation(
    conversation_id: int,
    service: RecommendationService = Depends(get_recommendation_service)
):
    results = service.list_recommendations_by_conversation(conversation_id)
    return results


@router.post("/{recommendation_id}/accept", response_model=RecommendationResponse)
def accept_recommendation(
    recommendation_id: int,
    service: RecommendationService = Depends(get_recommendation_service)
):
    existing = service.get_recommendation_by_id(recommendation_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    if existing["status"] != "pending":
        raise HTTPException(status_code=400, detail="Recommendation is not in pending status")
    
    result = service.accept_recommendation(recommendation_id)
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to accept recommendation")
    return result


@router.post("/{recommendation_id}/reject", response_model=RecommendationResponse)
def reject_recommendation(
    recommendation_id: int,
    service: RecommendationService = Depends(get_recommendation_service)
):
    existing = service.get_recommendation_by_id(recommendation_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    if existing["status"] != "pending":
        raise HTTPException(status_code=400, detail="Recommendation is not in pending status")
    
    result = service.reject_recommendation(recommendation_id)
    if result is None:
        raise HTTPException(status_code=400, detail="Failed to reject recommendation")
    return result
