"""Suggest reply generation chain."""

from typing import Optional
from app.ai.chains.model_factory import get_chat_model


class SuggestReplyChain:
    def __init__(self):
        self.model = get_chat_model(temperature=0.5)

    def generate(
        self,
        message: str,
        intent: str,
        context: Optional[dict] = None,
        kb_results: Optional[list[dict]] = None
    ) -> dict:
        used_tools = []
        
        if intent in ["order_query", "shipment_query", "after_sale_query"]:
            used_tools.append(f"get_{intent}")
        
        if intent == "faq" and kb_results:
            used_tools.append("search_kb")
            kb_context = "\n".join([r.get("content", "") for r in kb_results[:3]])
            prompt = f"用户问题: {message}\n\n知识库参考:\n{kb_context}\n\n请生成回复:"
            suggested_reply = self.model.invoke([{"role": "user", "content": prompt}])
        elif context:
            prompt = f"用户问题: {message}\n\n上下文: {context}\n\n请生成回复:"
            suggested_reply = self.model.invoke([{"role": "user", "content": prompt}])
        else:
            prompt = f"用户问题: {message}\n\n请生成回复:"
            suggested_reply = self.model.invoke([{"role": "user", "content": prompt}])
        
        risk_level = "low"
        if any(word in message.lower() for word in ["投诉", "退款", "退货"]):
            risk_level = "medium"
        
        return {
            "intent": intent,
            "confidence": 0.8,
            "suggested_reply": suggested_reply,
            "used_tools": used_tools,
            "risk_level": risk_level,
        }


def generate_suggestion(message: str, intent: str, context: Optional[dict] = None, kb_results: Optional[list[dict]] = None) -> dict:
    chain = SuggestReplyChain()
    return chain.generate(message, intent, context, kb_results)