from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.recommendation import (
    RecommendationCreateRequest,
    RecommendationResponse,
    AutoEvaluateRecommendationRequest,
    AutoEvaluateRecommendationResponse,
)
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


@router.post("/auto-evaluate", response_model=AutoEvaluateRecommendationResponse)
def auto_evaluate_recommendation(
    req: AutoEvaluateRecommendationRequest,
    db: Session = Depends(get_db),
    service: RecommendationService = Depends(get_recommendation_service),
):
    from app.services.context_aggregation_service import aggregate_conversation_context
    from app.services.recommendation_rule_service import evaluate_conversation_for_recommendation

    try:
        conv_id = int(req.conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid conversation_id")

    context = aggregate_conversation_context(db, conv_id)

    rec_payloads = evaluate_conversation_for_recommendation(
        conversation_context=context,
        conversation_id=conv_id,
        customer_id=req.customer_id,
        order_timeout_hours=req.order_timeout_hours or 24,
        after_sale_timeout_hours=req.after_sale_timeout_hours or 48,
    )

    created = []
    skipped = 0
    for payload in rec_payloads:
        existing_recs = service.list_recommendations_by_conversation(conv_id)
        duplicate = any(
            r["product_id"] == payload["product_id"]
            and r["status"] == "pending"
            and r.get("extra_json", {}).get("rule") == payload.get("extra_json", {}).get("rule")
            for r in existing_recs
        )
        if duplicate:
            skipped += 1
            continue

        result = service.create_recommendation(
            conversation_id=payload["conversation_id"],
            customer_id=payload["customer_id"],
            product_id=payload["product_id"],
            product_name=payload["product_name"],
            reason=payload.get("reason"),
            suggested_copy=payload.get("suggested_copy"),
            extra_json=payload.get("extra_json"),
        )
        if result:
            created.append(result)
        else:
            skipped += 1

    return {
        "created_recommendations": created,
        "skipped": skipped,
    }
