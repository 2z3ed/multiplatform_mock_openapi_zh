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

    def _fallback_reply(self, message: str, intent: str, context: Optional[dict] = None) -> str:
        """Rule-based fallback reply when LLM is unavailable."""
        context_info = ""
        if context and context.get("formatted"):
            context_info = context["formatted"]

        if intent == "order_query":
            if context_info:
                return f"您好，已为您查询到订单信息。{context_info[:100]}。如有其他问题请随时联系我们。"
            return "您好，已为您查询订单，请提供更多信息以便我们为您核实。"
        elif intent == "shipment_query":
            if context_info:
                return f"您好，已为您查询物流信息。{context_info[:100]}。请耐心等待，如有异常我们会及时通知。"
            return "您好，当前暂无物流信息，我们会尽快为您核实物流状态。"
        elif intent == "after_sale_query":
            if context_info:
                return f"您好，已为您查询售后信息。{context_info[:100]}。我们会尽快处理，请耐心等待。"
            return "您好，当前暂无可确认的售后信息，请提供售后单号以便我们核实。"
        elif intent == "inventory_query":
            if context_info:
                return f"您好，已为您查询库存。{context_info[:100]}。如需下单请尽快操作。"
            return "您好，当前暂无可确认的库存信息，请提供商品信息以便我们核实。"
        elif intent == "faq":
            return "您好，感谢您的咨询，我们正在为您核实相关信息。"
        else:
            return "您好，感谢您的消息，我们正在为您处理，请稍等。"

    def generate(
        self,
        message: str,
        intent: str,
        context: Optional[dict] = None,
        kb_results: Optional[list[dict]] = None
    ) -> dict:
        used_tools = []

        if intent in ["order_query", "shipment_query", "after_sale_query", "inventory_query"]:
            used_tools.append(f"get_{intent}")

        context_info = ""
        if context and context.get("formatted"):
            context_info = context["formatted"]
        elif intent == "order_query" and context:
            status = context.get("status_name", context.get("status", "未知"))
            order_id = context.get("order_id", context.get("internal_order_id", ""))
            context_info = f"订单状态: {status}"
            if context.get("internal_order_id"):
                context_info += f"，内部订单ID: {context['internal_order_id']}"
        elif intent == "shipment_query" and context:
            if context.get("resolved"):
                status = context.get("shipment_status", "未知")
                tracking = context.get("tracking_no", "")
                carrier = context.get("carrier", "")
                source = context.get("source", "unknown")
                parts = [f"物流状态: {status}"]
                if tracking:
                    parts.append(f"运单号: {tracking}")
                if carrier:
                    parts.append(f"物流公司: {carrier}")
                if context.get("internal_order_id"):
                    parts.append(f"内部订单ID: {context['internal_order_id']}")
                parts.append(f"数据来源: {source}")
                context_info = "，".join(parts)
            else:
                shipments = context.get("shipments", [])
                if shipments:
                    s = shipments[0]
                    context_info = f"物流状态: {s.get('status_name', s.get('status', '未知'))}"
                else:
                    context_info = "当前暂无可确认的物流信息"
        elif intent == "after_sale_query" and context:
            if context.get("resolved"):
                status = context.get("after_sale_status", context.get("status_name", "未知"))
                atype = context.get("after_sale_type", context.get("type_name", ""))
                amount = context.get("apply_amount", "")
                approve = context.get("approve_amount", "")
                reason = context.get("reason", "")
                source = context.get("source", "unknown")
                parts = [f"售后状态: {status}"]
                if atype:
                    parts.append(f"类型: {atype}")
                if amount:
                    parts.append(f"申请金额: {amount}")
                if approve:
                    parts.append(f"审核金额: {approve}")
                if reason:
                    parts.append(f"原因: {reason}")
                if context.get("internal_order_id"):
                    parts.append(f"内部订单ID: {context['internal_order_id']}")
                parts.append(f"数据来源: {source}")
                context_info = "，".join(parts)
            else:
                after_sales = context.get("after_sales", [])
                if after_sales:
                    parts = []
                    for i, as_item in enumerate(after_sales[:2]):
                        prefix = f"售后{i+1}" if len(after_sales) > 1 else "售后"
                        status = as_item.get("status_name", as_item.get("status", "未知"))
                        parts.append(f"{prefix}状态: {status}")
                        if as_item.get("type_name"):
                            parts.append(f"{prefix}类型: {as_item['type_name']}")
                        if as_item.get("apply_amount"):
                            parts.append(f"{prefix}金额: ¥{as_item['apply_amount']}")
                        if as_item.get("reason"):
                            parts.append(f"{prefix}原因: {as_item['reason']}")
                    context_info = "，".join(parts)
                else:
                    status = context.get("status_name", context.get("status", "未知"))
                    if status != "未知":
                        context_info = f"售后状态: {status}"
                    else:
                        context_info = "当前暂无可确认的售后信息"
        elif intent == "inventory_query" and context:
            if context.get("resolved"):
                items = context.get("items", [])
                if items:
                    parts = []
                    for item in items[:5]:
                        name = item.get("product_name", item.get("sku_id", ""))
                        stock = item.get("stock_state", "未知")
                        qty = item.get("quantity", 0)
                        parts.append(f"{name}: {stock} ({qty}件)")
                    context_info = "库存信息: " + "，".join(parts)
                else:
                    context_info = "当前暂无可确认的库存信息"
            else:
                items = context.get("items", [])
                if items:
                    parts = []
                    for item in items[:5]:
                        name = item.get("product_name", item.get("sku_id", ""))
                        stock = item.get("stock_state", "未知")
                        qty = item.get("quantity", 0)
                        parts.append(f"{name}: {stock} ({qty}件)")
                    context_info = "库存信息: " + "，".join(parts)
                else:
                    context_info = "当前暂无可确认的库存信息"

        risk_level = "low"
        if any(word in message.lower() for word in ["投诉", "退款", "退货"]):
            risk_level = "medium"

        llm_used = True
        if intent == "faq" and kb_results:
            used_tools.append("search_kb")
            kb_context = "\n".join([r.get("content", "") for r in kb_results[:3]])
            prompt = f"{SYSTEM_PROMPT}\n\n用户问题: {message}\n\n知识库参考:\n{kb_context}\n\n请直接生成客服回复："
            try:
                suggested_reply = self.model.invoke([
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"用户问题: {message}\n\n知识库参考:\n{kb_context}\n\n请直接生成客服回复："}
                ])
            except Exception as e:
                print(f"LLM call failed: {e}")
                suggested_reply = self._fallback_reply(message, intent, context)
                llm_used = False
        elif context_info:
            prompt = f"{SYSTEM_PROMPT}\n\n用户问题: {message}\n\n查询结果: {context_info}\n\n请直接生成客服回复："
            try:
                suggested_reply = self.model.invoke([
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"用户问题: {message}\n\n查询结果: {context_info}\n\n请直接生成客服回复："}
                ])
            except Exception as e:
                print(f"LLM call failed: {e}")
                suggested_reply = self._fallback_reply(message, intent, context)
                llm_used = False
        else:
            prompt = f"{SYSTEM_PROMPT}\n\n用户问题: {message}\n\n请直接生成客服回复："
            try:
                suggested_reply = self.model.invoke([
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"用户问题: {message}\n\n请直接生成客服回复："}
                ])
            except Exception as e:
                print(f"LLM call failed: {e}")
                suggested_reply = self._fallback_reply(message, intent, context)
                llm_used = False

        source_summary = context.get("formatted", "") if context and context.get("formatted") else ""

        return {
            "intent": intent,
            "confidence": 0.8 if llm_used else 0.6,
            "suggested_reply": suggested_reply,
            "used_tools": used_tools,
            "risk_level": risk_level,
            "source_summary": source_summary,
            "degraded": not llm_used,
            "fallback_reason": None if llm_used else "llm_unavailable",
        }


def generate_suggestion(message: str, intent: str, context: Optional[dict] = None, kb_results: Optional[list[dict]] = None) -> dict:
    chain = SuggestReplyChain()
    return chain.generate(message, intent, context, kb_results)