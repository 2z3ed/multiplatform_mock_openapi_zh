"""Suggest reply generation chain."""

from typing import Optional
from app.ai.chains.model_factory import get_chat_model

SYSTEM_PROMPT = """你是一位专业的电商客服。你的回复将直接发送给客户，请遵循以下规则：

1. 直接回答客户问题，不要罗列内部字段
2. 语气自然、礼貌、简洁，像真人客服一样
3. 只保留必要信息，不要暴露：
   - 内部工具名（如 get_order）
   - UTC 时间、平台名、买家手机号等隐私
   - 金额不一致、数据异常等排查信息
4. 一句话说清结果，然后给一句自然的下一步引导
5. 总长度控制在 100 字以内

禁止输出格式化的字段列表。"""


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

        context_info = ""
        if intent == "order_query" and context:
            status = context.get("status_name", context.get("status", "未知"))
            order_id = context.get("order_id", "")
            context_info = f"订单状态: {status}"
        elif intent == "shipment_query" and context:
            shipments = context.get("shipments", [])
            if shipments:
                s = shipments[0]
                context_info = f"物流状态: {s.get('status_name', s.get('status', '未知'))}"
            else:
                context_info = "暂无物流信息"
        elif intent == "after_sale_query" and context:
            status = context.get("status_name", context.get("status", "未知"))
            context_info = f"售后状态: {status}"

        if intent == "faq" and kb_results:
            used_tools.append("search_kb")
            kb_context = "\n".join([r.get("content", "") for r in kb_results[:3]])
            prompt = f"{SYSTEM_PROMPT}\n\n用户问题: {message}\n\n知识库参考:\n{kb_context}\n\n请直接生成客服回复："
            suggested_reply = self.model.invoke([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"用户问题: {message}\n\n知识库参考:\n{kb_context}\n\n请直接生成客服回复："}
            ])
        elif context_info:
            prompt = f"{SYSTEM_PROMPT}\n\n用户问题: {message}\n\n查询结果: {context_info}\n\n请直接生成客服回复："
            suggested_reply = self.model.invoke([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"用户问题: {message}\n\n查询结果: {context_info}\n\n请直接生成客服回复："}
            ])
        else:
            prompt = f"{SYSTEM_PROMPT}\n\n用户问题: {message}\n\n请直接生成客服回复："
            suggested_reply = self.model.invoke([
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"用户问题: {message}\n\n请直接生成客服回复："}
            ])

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