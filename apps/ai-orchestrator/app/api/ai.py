from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
import random

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
    source_summary: str | None = None
    degraded: bool = False
    fallback_reason: str | None = None


class UserReplyRequest(BaseModel):
    conversation_id: str
    agent_message: str
    platform: str = "jd"


class UserReplyResponse(BaseModel):
    reply: str
    intent: str
    emotion: str


USER_REPLY_TEMPLATES = {
    "jd": [
        "好的，谢谢你的回复",
        "那大概什么时候能到呢？",
        "好的，我再等等看",
        "那退款什么时候能到账？",
        "明白了，有消息通知我一下",
        "好的，那帮我催一下快递吧",
        "收到，谢谢",
    ],
    "taobao": [
        "好的亲，谢谢",
        "那什么时候发货呢？",
        "好的，我等一下",
        "退款大概几天能到？",
        "知道了，有物流更新告诉我",
        "好的，帮我查一下快递",
        "收到",
    ],
    "douyin_shop": [
        "好的谢谢",
        "那什么时候能发货？",
        "好的我等等",
        "退款多久能到？",
        "知道了，有消息通知我",
        "好的帮我催一下",
        "收到谢谢",
    ],
    "wecom_kf": [
        "好的，谢谢您的回复",
        "请问大概什么时候能处理完？",
        "好的，我等您的通知",
        "明白了，有进展告诉我一下",
        "收到，感谢",
    ],
}


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


@router.post("/user-reply", response_model=UserReplyResponse)
async def user_reply(req: UserReplyRequest) -> UserReplyResponse:
    from app.ai.chains.model_factory import get_chat_model
    
    platform = req.platform
    templates = USER_REPLY_TEMPLATES.get(platform, USER_REPLY_TEMPLATES["jd"])
    
    try:
        model = get_chat_model(temperature=0.7)
        
        system_prompt = f"""你是用户模拟器，模拟真实用户回复客服消息。
用户说话风格：直接、口语、简短、有目的性。

绝对禁止：
- 禁止出现"亲"字 - 这是客服用语
- 禁止"请问"、"麻烦"、"您好" - 太客气
- 禁止"~"符号 - 不自然

正确示例：
- 好的谢谢
- 那大概什么时候能到
- 知道了
- 退款什么时候到账
- 好的我等等

只输出用户回复的内容，不要其他解释。"""

        user_prompt = f"客服说：{req.agent_message}\n\n请用简短自然的口语回复："
        
        response = model.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        reply = response.strip() if response else random.choice(templates)
        
        return UserReplyResponse(
            reply=reply,
            intent="response",
            emotion="calm"
        )
    except Exception as e:
        print(f"User reply generation failed: {e}")
        return UserReplyResponse(
            reply=random.choice(templates),
            intent="response",
            emotion="calm"
        )