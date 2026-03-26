from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os

router = APIRouter(prefix="/api/ai", tags=["ai"])

DOMAIN_SERVICE_URL = os.getenv("DOMAIN_SERVICE_URL", "http://domain-service:8001")


class SuggestReplyRequest(BaseModel):
    conversation_id: str
    message: str
    platform: str = "jd"
    order_id: str | None = None


class SuggestReplyResponse(BaseModel):
    intent: str
    confidence: float
    suggested_reply: str
    used_tools: list[str]
    risk_level: str
    needs_human_review: bool


@router.post("/suggest-reply", response_model=SuggestReplyResponse)
def suggest_reply(req: SuggestReplyRequest) -> SuggestReplyResponse:
    from app.ai.graphs.suggest_reply_graph import run_suggest_reply_graph
    
    result = run_suggest_reply_graph(
        conversation_id=req.conversation_id,
        message=req.message,
        platform=req.platform,
        order_id=req.order_id
    )
    
    try:
        httpx.post(
            f"{DOMAIN_SERVICE_URL}/api/audit-logs",
            json={
                "action": "ai_suggestion_generated",
                "actor_type": "ai",
                "actor_id": "ai-orchestrator",
                "target_type": "conversation",
                "target_id": req.conversation_id,
                "detail": f"Generated suggestion for intent: {result['intent']}",
                "detail_json": {"intent": result["intent"], "confidence": result["confidence"]}
            },
            timeout=5
        )
    except Exception:
        pass
    
    return SuggestReplyResponse(**result)