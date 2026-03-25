from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/ai", tags=["ai"])


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
    
    return SuggestReplyResponse(**result)