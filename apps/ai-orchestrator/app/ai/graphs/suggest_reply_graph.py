"""LangGraph suggest_reply_graph for V1.

Required nodes:
- load_context
- classify_intent
- route_to_tool_or_kb
- build_prompt_context
- generate_suggestion
- human_review_interrupt

Note: human_review_interrupt is a special node that stops the graph
and returns control to the human agent. The graph does NOT auto-send.
"""

from typing import TypedDict, Optional
import httpx
import os
from app.ai.chains.intent_chain import classify_intent
from app.ai.chains.suggest_reply_chain import generate_suggestion
from app.ai.tools.order_tools import get_order
from app.ai.tools.shipment_tools import get_shipment
from app.ai.tools.after_sale_tools import get_after_sale
from app.ai.tools.kb_tools import search_kb

DOMAIN_SERVICE_URL = os.getenv("DOMAIN_SERVICE_URL", "http://domain-service:8001")


class GraphState(TypedDict):
    conversation_id: str
    message: str
    platform: Optional[str]
    order_id: Optional[str]
    context: Optional[dict]
    conversation_context: Optional[dict]
    prompt_context: Optional[str]
    intent: Optional[str]
    confidence: Optional[float]
    route: Optional[str]
    kb_results: Optional[list[dict]]
    suggested_reply: Optional[str]
    used_tools: list[str]
    risk_level: Optional[str]
    needs_human_review: bool
    explain_status: Optional[dict]


def _fetch_conversation_context(conversation_id: str) -> Optional[dict]:
    """Fetch real business facts from the completed conversation context API."""
    try:
        response = httpx.get(
            f"{DOMAIN_SERVICE_URL}/api/conversations/{conversation_id}/context",
            timeout=5,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def _fetch_explain_status(conversation_id: str) -> Optional[dict]:
    """Fetch structured explanations from the domain-service explain endpoint."""
    try:
        response = httpx.post(
            f"{DOMAIN_SERVICE_URL}/api/integration/explain/conversation",
            json={"conversation_id": conversation_id},
            timeout=5,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return None


def _resolve_order_from_context(conversation_context: Optional[dict]) -> Optional[dict]:
    """Extract the first linked order's platform + external_order_id from conversation context."""
    if not conversation_context:
        return None
    orders = conversation_context.get("orders", [])
    if not orders:
        return None
    first = orders[0]
    platform = first.get("platform")
    external_order_id = first.get("external_order_id")
    if platform and external_order_id:
        return {
            "platform": platform,
            "order_id": external_order_id,
            "order": first.get("order"),
            "shipment": first.get("shipment"),
            "after_sales": first.get("after_sales", []),
            "inventory": first.get("inventory"),
        }
    return None


def load_context(state: GraphState) -> GraphState:
    conversation_id = state.get("conversation_id", "")
    conversation_context = _fetch_conversation_context(conversation_id)
    resolved_order = _resolve_order_from_context(conversation_context)

    updates: dict = {
        "conversation_context": conversation_context,
    }

    if resolved_order:
        current_platform = state.get("platform")
        if not current_platform and resolved_order.get("platform"):
            updates["platform"] = resolved_order["platform"]
        current_order_id = state.get("order_id")
        if not current_order_id and resolved_order.get("order_id"):
            updates["order_id"] = resolved_order["order_id"]

    return {
        **state,
        **updates,
    }


def explain_status_node(state: GraphState) -> GraphState:
    """Call the domain-service explain endpoint to get structured explanations."""
    conversation_id = state.get("conversation_id", "")
    explain_result = _fetch_explain_status(conversation_id)

    if explain_result and explain_result.get("formatted"):
        return {
            **state,
            "explain_status": explain_result,
        }
    return {
        **state,
        "explain_status": None,
    }


def classify_intent_node(state: GraphState) -> GraphState:
    message = state.get("message", "")
    result = classify_intent(message)
    return {
        **state,
        "intent": result["intent"],
        "confidence": result.get("confidence", 0.0),
    }


def route_to_tool_or_kb(state: GraphState) -> GraphState:
    intent = state.get("intent", "unknown")
    conversation_context = state.get("conversation_context")
    resolved_order = _resolve_order_from_context(conversation_context)

    if intent == "order_query":
        if resolved_order and resolved_order.get("order"):
            context = {
                "source": "conversation_context",
                **resolved_order["order"],
            }
            return {
                **state,
                "route": "tool",
                "context": context,
                "used_tools": state.get("used_tools", []) + ["get_order"],
            }
        order_id = state.get("order_id") or "JD20240315001"
        context = get_order(order_id, state.get("platform") or "jd")
        return {
            **state,
            "route": "tool",
            "context": context,
            "used_tools": state.get("used_tools", []) + ["get_order"],
        }
    elif intent == "shipment_query":
        if resolved_order and resolved_order.get("shipment"):
            context = {
                "source": "conversation_context",
                **resolved_order["shipment"],
            }
            return {
                **state,
                "route": "tool",
                "context": context,
                "used_tools": state.get("used_tools", []) + ["get_shipment"],
            }
        order_id = state.get("order_id") or "JD20240315001"
        context = get_shipment(order_id, state.get("platform") or "jd")
        return {
            **state,
            "route": "tool",
            "context": context,
            "used_tools": state.get("used_tools", []) + ["get_shipment"],
        }
    elif intent == "after_sale_query":
        after_sales = []
        if resolved_order:
            after_sales = resolved_order.get("after_sales", [])
        if after_sales:
            context = {
                "source": "conversation_context",
                "after_sales": after_sales,
            }
            return {
                **state,
                "route": "tool",
                "context": context,
                "used_tools": state.get("used_tools", []) + ["get_after_sale"],
            }
        after_sale_id = state.get("order_id") or "AS20240320001"
        order_id = state.get("order_id")
        context = get_after_sale(after_sale_id, state.get("platform") or "jd", order_id=order_id)
        return {
            **state,
            "route": "tool",
            "context": context,
            "used_tools": state.get("used_tools", []) + ["get_after_sale"],
        }
    elif intent == "inventory_query":
        if resolved_order and resolved_order.get("inventory"):
            context = {
                "source": "conversation_context",
                **resolved_order["inventory"],
            }
            return {
                **state,
                "route": "tool",
                "context": context,
                "used_tools": state.get("used_tools", []) + ["get_inventory"],
            }
        return {
            **state,
            "route": "none",
            "context": {},
        }
    elif intent == "faq":
        kb_results = search_kb(state.get("message", ""), top_k=3)
        return {
            **state,
            "route": "kb",
            "kb_results": kb_results.get("results", []),
            "used_tools": state.get("used_tools", []) + ["search_kb"],
        }
    else:
        if resolved_order:
            return {
                **state,
                "route": "context",
                "context": {
                    "source": "conversation_context",
                    "order": resolved_order.get("order"),
                    "shipment": resolved_order.get("shipment"),
                    "after_sales": resolved_order.get("after_sales", []),
                    "inventory": resolved_order.get("inventory"),
                },
            }
        return {
            **state,
            "route": "none",
            "context": {},
        }


def build_prompt_context(state: GraphState) -> GraphState:
    route = state.get("route", "none")
    context = state.get("context", {})
    kb_results = state.get("kb_results", [])
    explain_status = state.get("explain_status")

    prompt_context = ""
    if explain_status and explain_status.get("formatted"):
        prompt_context = explain_status["formatted"]
    elif route == "tool" and context:
        source = context.get("source", "")
        if source == "conversation_context":
            parts = []
            order = context.get("order")
            if order:
                status_name = order.get("status_name", order.get("status", "未知"))
                order_id = order.get("order_id", "")
                amount = order.get("payment_amount", "")
                receiver = order.get("receiver_name", "")
                items = order.get("items", [])
                parts.append(f"订单状态: {status_name}")
                if order_id:
                    parts.append(f"订单号: {order_id}")
                if amount:
                    parts.append(f"实付金额: ¥{amount}")
                if receiver:
                    parts.append(f"收货人: {receiver}")
                if items:
                    item_summary = ", ".join(
                        f"{i.get('sku_name', '')}x{i.get('quantity', 0)}"
                        for i in items[:5]
                    )
                    parts.append(f"商品: {item_summary}")
            shipment = context.get("shipment")
            if shipment and shipment.get("shipments"):
                s = shipment["shipments"][0]
                parts.append(f"物流状态: {s.get('status_name', s.get('status', '未知'))}")
                if s.get("express_company"):
                    parts.append(f"快递公司: {s['express_company']}")
                if s.get("express_no"):
                    parts.append(f"运单号: {s['express_no']}")
                if s.get("trace"):
                    latest = s["trace"][0]
                    parts.append(f"最新物流: {latest.get('message', '')}")
                    if latest.get("time"):
                        parts.append(f"物流时间: {latest['time']}")
            after_sales = context.get("after_sales", [])
            if after_sales:
                for i, as_item in enumerate(after_sales[:2]):
                    prefix = f"售后{i+1}" if len(after_sales) > 1 else "售后"
                    parts.append(f"{prefix}状态: {as_item.get('status_name', as_item.get('status', '未知'))}")
                    if as_item.get("type_name"):
                        parts.append(f"{prefix}类型: {as_item['type_name']}")
                    if as_item.get("apply_amount"):
                        parts.append(f"{prefix}金额: ¥{as_item['apply_amount']}")
                    if as_item.get("reason"):
                        parts.append(f"{prefix}原因: {as_item['reason']}")
            inventory = context.get("inventory")
            if inventory and inventory.get("items"):
                for inv_item in inventory["items"][:5]:
                    stock = inv_item.get("stock_state", "")
                    qty = inv_item.get("quantity", 0)
                    name = inv_item.get("product_name", inv_item.get("sku_id", ""))
                    parts.append(f"库存 {name}: {stock} ({qty}件)")
            prompt_context = "，".join(parts)
        else:
            prompt_context = f"订单信息: {context}"
    elif route == "context" and context:
        parts = []
        order = context.get("order")
        if order:
            status_name = order.get("status_name", order.get("status", "未知"))
            order_id = order.get("order_id", "")
            amount = order.get("payment_amount", "")
            receiver = order.get("receiver_name", "")
            items = order.get("items", [])
            parts.append(f"订单状态: {status_name}")
            if order_id:
                parts.append(f"订单号: {order_id}")
            if amount:
                parts.append(f"实付金额: ¥{amount}")
            if receiver:
                parts.append(f"收货人: {receiver}")
            if items:
                item_summary = ", ".join(
                    f"{i.get('sku_name', '')}x{i.get('quantity', 0)}"
                    for i in items[:5]
                )
                parts.append(f"商品: {item_summary}")
        shipment = context.get("shipment")
        if shipment and shipment.get("shipments"):
            s = shipment["shipments"][0]
            parts.append(f"物流状态: {s.get('status_name', s.get('status', '未知'))}")
            if s.get("express_company"):
                parts.append(f"快递公司: {s['express_company']}")
            if s.get("express_no"):
                parts.append(f"运单号: {s['express_no']}")
            if s.get("trace"):
                latest = s["trace"][0]
                parts.append(f"最新物流: {latest.get('message', '')}")
                if latest.get("time"):
                    parts.append(f"物流时间: {latest['time']}")
        after_sales = context.get("after_sales", [])
        if after_sales:
            for i, as_item in enumerate(after_sales[:2]):
                prefix = f"售后{i+1}" if len(after_sales) > 1 else "售后"
                parts.append(f"{prefix}状态: {as_item.get('status_name', as_item.get('status', '未知'))}")
                if as_item.get("apply_amount"):
                    parts.append(f"{prefix}金额: ¥{as_item['apply_amount']}")
                if as_item.get("reason"):
                    parts.append(f"{prefix}原因: {as_item['reason']}")
        inventory = context.get("inventory")
        if inventory and inventory.get("items"):
            for inv_item in inventory["items"][:5]:
                stock = inv_item.get("stock_state", "")
                qty = inv_item.get("quantity", 0)
                name = inv_item.get("product_name", inv_item.get("sku_id", ""))
                parts.append(f"库存 {name}: {stock} ({qty}件)")
        prompt_context = "，".join(parts) if parts else ""
    elif route == "kb" and kb_results:
        kb_text = "\n".join([r.get("content", "") for r in kb_results])
        prompt_context = f"知识库参考:\n{kb_text}"

    return {
        **state,
        "prompt_context": prompt_context,
    }


def generate_suggestion_node(state: GraphState) -> GraphState:
    message = state.get("message", "")
    intent = state.get("intent", "unknown")
    context = state.get("context", {})
    kb_results = state.get("kb_results", [])
    prompt_context = state.get("prompt_context", "")
    used_tools = state.get("used_tools", [])

    enriched_context = None
    if prompt_context:
        enriched_context = {"formatted": prompt_context}
    elif context:
        enriched_context = context

    result = generate_suggestion(message, intent or "unknown", enriched_context, kb_results)
    
    return {
        **state,
        "suggested_reply": result["suggested_reply"],
        "confidence": result.get("confidence", 0.0),
        "risk_level": result.get("risk_level", "low"),
        "used_tools": used_tools,
        "needs_human_review": True,
        "degraded": result.get("degraded", False),
        "fallback_reason": result.get("fallback_reason"),
    }


def human_review_interrupt(state: GraphState) -> GraphState:
    return {
        **state,
        "needs_human_review": True,
    }


def run_suggest_reply_graph(
    conversation_id: str,
    message: str,
    platform: str = "jd",
    order_id: str | None = None
) -> dict:
    initial_state: GraphState = {
        "conversation_id": conversation_id,
        "message": message,
        "platform": platform,
        "order_id": order_id,
        "context": None,
        "conversation_context": None,
        "prompt_context": None,
        "intent": None,
        "confidence": None,
        "route": None,
        "kb_results": None,
        "suggested_reply": None,
        "used_tools": [],
        "risk_level": None,
        "needs_human_review": False,
        "explain_status": None,
    }
    
    state = load_context(initial_state)
    state = explain_status_node(state)
    state = classify_intent_node(state)
    state = route_to_tool_or_kb(state)
    state = build_prompt_context(state)
    state = generate_suggestion_node(state)
    state = human_review_interrupt(state)
    
    return {
        "intent": state["intent"],
        "confidence": state["confidence"],
        "suggested_reply": state["suggested_reply"],
        "used_tools": state["used_tools"],
        "risk_level": state["risk_level"],
        "needs_human_review": state["needs_human_review"],
        "source_summary": state["explain_status"].get("formatted") if state.get("explain_status") else None,
        "degraded": state.get("degraded", False),
        "fallback_reason": state.get("fallback_reason"),
    }