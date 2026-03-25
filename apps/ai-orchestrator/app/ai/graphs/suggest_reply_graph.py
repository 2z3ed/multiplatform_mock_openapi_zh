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
from app.ai.chains.intent_chain import classify_intent
from app.ai.chains.suggest_reply_chain import generate_suggestion
from app.ai.tools.order_tools import get_order
from app.ai.tools.shipment_tools import get_shipment
from app.ai.tools.after_sale_tools import get_after_sale
from app.ai.tools.kb_tools import search_kb


class GraphState(TypedDict):
    conversation_id: str
    message: str
    platform: Optional[str]
    order_id: Optional[str]
    context: Optional[dict]
    intent: Optional[str]
    confidence: Optional[float]
    route: Optional[str]
    kb_results: Optional[list[dict]]
    suggested_reply: Optional[str]
    used_tools: list[str]
    risk_level: Optional[str]
    needs_human_review: bool


def load_context(state: GraphState) -> GraphState:
    conversation_id = state.get("conversation_id", "")
    return {
        **state,
        "context": {"conversation_id": conversation_id},
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
    
    if intent == "order_query":
        order_id = state.get("order_id") or "JD20240315001"
        context = get_order(order_id, state.get("platform", "jd"))
        return {
            **state,
            "route": "tool",
            "context": context,
            "used_tools": state.get("used_tools", []) + ["get_order"],
        }
    elif intent == "shipment_query":
        order_id = state.get("order_id") or "JD20240315001"
        context = get_shipment(order_id, state.get("platform", "jd"))
        return {
            **state,
            "route": "tool",
            "context": context,
            "used_tools": state.get("used_tools", []) + ["get_shipment"],
        }
    elif intent == "after_sale_query":
        after_sale_id = state.get("order_id") or "AS20240320001"
        context = get_after_sale(after_sale_id, state.get("platform", "jd"))
        return {
            **state,
            "route": "tool",
            "context": context,
            "used_tools": state.get("used_tools", []) + ["get_after_sale"],
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
        return {
            **state,
            "route": "none",
            "context": {},
        }


def build_prompt_context(state: GraphState) -> GraphState:
    route = state.get("route", "none")
    context = state.get("context", {})
    kb_results = state.get("kb_results", [])
    
    prompt_context = ""
    if route == "tool" and context:
        prompt_context = f"订单信息: {context}"
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
    used_tools = state.get("used_tools", [])
    
    result = generate_suggestion(message, intent, context if context else None, kb_results)
    
    return {
        **state,
        "suggested_reply": result["suggested_reply"],
        "confidence": result.get("confidence", 0.0),
        "risk_level": result.get("risk_level", "low"),
        "used_tools": used_tools,
        "needs_human_review": True,
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
        "intent": None,
        "confidence": None,
        "route": None,
        "kb_results": None,
        "suggested_reply": None,
        "used_tools": [],
        "risk_level": None,
        "needs_human_review": False,
    }
    
    state = load_context(initial_state)
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
    }