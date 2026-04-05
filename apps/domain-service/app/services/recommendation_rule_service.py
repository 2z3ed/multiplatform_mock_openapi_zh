"""
Recommendation rule service: evaluates real business facts and auto-creates Recommendations.

Rules:
1. inventory_shortage → recommend refund / wait restock / exchange
2. shipment_pending_timeout → recommend urge shipment / appease
3. after_sale_processing_timeout → recommend escalate / follow up
"""
from datetime import datetime, timedelta
from typing import Optional


DEFAULT_ORDER_TIMEOUT_HOURS = 24
DEFAULT_AFTER_SALE_TIMEOUT_HOURS = 48


def _parse_time(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is not None:
            dt = dt.replace(tzinfo=None)
        return dt
    except (ValueError, TypeError):
        return None


def _hours_since(dt: Optional[datetime], now: Optional[datetime] = None) -> Optional[float]:
    if dt is None:
        return None
    ref = now or datetime.utcnow()
    delta = ref - dt
    return delta.total_seconds() / 3600


def evaluate_inventory_shortage(
    order: Optional[dict],
    inventory: Optional[dict],
    conversation_id: int,
    customer_id: int,
    platform: Optional[str] = None,
) -> list[dict]:
    """
    Rule 1: If any SKU is out_of_stock or low_stock, recommend appropriate action.
    """
    recommendations = []
    if not inventory or not inventory.get("items"):
        return recommendations

    order_status = ""
    if order:
        order_status = (order.get("status") or "").lower()

    for item in inventory.get("items", [])[:3]:
        stock_state = (item.get("stock_state") or "").lower()
        if stock_state not in ("out_of_stock", "low_stock"):
            continue

        product_name = item.get("product_name", item.get("sku_id", "未知商品"))
        sku_id = item.get("sku_id", "")
        quantity = item.get("quantity", 0)
        warehouse_name = item.get("warehouse_name", "")

        if stock_state == "out_of_stock":
            recommended_action = "refund_or_exchange"
            reason = f"{product_name} 当前缺货（库存 {quantity} 件）"
            suggested_copy = (
                f"您好，您咨询的 {product_name} 目前暂时缺货。"
                f"我们可以为您办理退款，或为您推荐同类替代商品，请问您更倾向哪种方案？"
            )
            priority = "high"
        else:
            recommended_action = "wait_or_exchange"
            reason = f"{product_name} 库存紧张（仅剩 {quantity} 件）"
            suggested_copy = (
                f"您好，{product_name} 目前库存较为紧张，"
                f"建议您尽快下单。如需换货或补发，我们也可以为您安排。"
            )
            priority = "medium"

        product_id = sku_id or f"inv_{item.get('product_id', '')}"
        extra_json = {
            "platform": platform,
            "rule": "inventory_shortage",
            "stock_state": stock_state,
            "quantity": quantity,
            "warehouse_name": warehouse_name,
            "order_status": order_status,
            "recommended_action": recommended_action,
        }

        recommendations.append({
            "customer_id": customer_id,
            "conversation_id": conversation_id,
            "product_id": product_id,
            "product_name": product_name,
            "reason": reason,
            "suggested_copy": suggested_copy,
            "extra_json": extra_json,
            "priority": priority,
        })

    return recommendations


def evaluate_shipment_pending_timeout(
    order: Optional[dict],
    shipment: Optional[dict],
    conversation_id: int,
    customer_id: int,
    platform: Optional[str] = None,
    timeout_hours: int = DEFAULT_ORDER_TIMEOUT_HOURS,
    now: Optional[datetime] = None,
) -> Optional[dict]:
    """
    Rule 2: If order is paid but not shipped beyond threshold, recommend urge/appease.
    """
    if not order:
        return None

    status = (order.get("status") or "").lower()
    pending_shipment_statuses = {
        "wait_seller_send_goods", "paid", "pending_shipment",
    }
    if status not in pending_shipment_statuses:
        return None

    order_id = order.get("order_id", "")
    if not order_id:
        return None

    pay_time = _parse_time(order.get("pay_time")) or _parse_time(order.get("create_time"))
    elapsed = _hours_since(pay_time, now)
    if elapsed is None or elapsed < timeout_hours:
        return None

    status_name = order.get("status_name", order.get("status", "未知"))
    total_amount = order.get("total_amount") or order.get("payment_amount", "")
    receiver_name = order.get("receiver_name", "")

    if elapsed >= timeout_hours * 2:
        recommended_action = "urge_shipment"
        reason = f"订单 {order_id} 已付款 {int(elapsed)} 小时仍未发货（阈值 {timeout_hours}h）"
        suggested_copy = (
            f"您好，您的订单 {order_id} 目前状态为「{status_name}」，"
            f"已等待约 {int(elapsed)} 小时。我们已为您加急催发货，"
            f"预计尽快安排发出，给您带来不便深表歉意。"
        )
        priority = "high"
    else:
        recommended_action = "appease"
        reason = f"订单 {order_id} 已付款 {int(elapsed)} 小时，接近发货时限"
        suggested_copy = (
            f"您好，您的订单 {order_id} 目前状态为「{status_name}」，"
            f"我们已安排仓库尽快处理，预计今天内发出，请耐心等待。"
        )
        priority = "medium"

    extra_json = {
        "platform": platform,
        "rule": "shipment_pending_timeout",
        "order_id": order_id,
        "order_status": status,
        "order_status_name": status_name,
        "pay_time": order.get("pay_time"),
        "create_time": order.get("create_time"),
        "elapsed_hours": round(elapsed, 1),
        "timeout_hours": timeout_hours,
        "recommended_action": recommended_action,
        "has_shipment": bool(shipment and shipment.get("shipments")),
    }

    return {
        "customer_id": customer_id,
        "conversation_id": conversation_id,
        "product_id": order_id,
        "product_name": f"订单 {order_id}",
        "reason": reason,
        "suggested_copy": suggested_copy,
        "extra_json": extra_json,
        "priority": priority,
    }


def evaluate_after_sale_processing_timeout(
    after_sale: dict,
    conversation_id: int,
    customer_id: int,
    platform: Optional[str] = None,
    timeout_hours: int = DEFAULT_AFTER_SALE_TIMEOUT_HOURS,
    now: Optional[datetime] = None,
) -> Optional[dict]:
    """
    Rule 3: If after-sale is processing beyond threshold, recommend escalate/follow-up.
    """
    if not after_sale:
        return None

    status = (after_sale.get("status") or "").lower()
    processing_statuses = {
        "processing", "under_review", "in_progress",
        "apply", "pending", "waiting_for_seller",
    }
    if status not in processing_statuses:
        return None

    after_sale_id = after_sale.get("after_sale_id", "")
    order_id = after_sale.get("order_id", "")
    if not after_sale_id:
        return None

    apply_time = _parse_time(after_sale.get("apply_time"))
    elapsed = _hours_since(apply_time, now)
    if elapsed is None or elapsed < timeout_hours:
        return None

    status_name = after_sale.get("status_name", after_sale.get("status", "未知"))
    type_name = after_sale.get("type_name", "")
    reason_text = after_sale.get("reason", "")
    apply_amount = after_sale.get("apply_amount", "")

    if elapsed >= timeout_hours * 2:
        recommended_action = "escalate"
        reason = f"售后 {after_sale_id} 已处理 {int(elapsed)} 小时仍未完成（阈值 {timeout_hours}h）"
        suggested_copy = (
            f"您好，关于您的售后申请 {after_sale_id}，"
            f"目前状态为「{status_name}」。我们已将您的申请升级为加急处理，"
            f"预计 24 小时内给您明确反馈。"
        )
        priority = "high"
    else:
        recommended_action = "follow_up"
        reason = f"售后 {after_sale_id} 处理中，已等待 {int(elapsed)} 小时"
        suggested_copy = (
            f"您好，关于您的售后申请 {after_sale_id}，"
            f"目前状态为「{status_name}」，我们正在积极处理中，"
            f"预计尽快给您反馈，请耐心等待。"
        )
        priority = "medium"

    extra_json = {
        "platform": platform,
        "rule": "after_sale_processing_timeout",
        "after_sale_id": after_sale_id,
        "order_id": order_id or None,
        "after_sale_status": status,
        "after_sale_status_name": status_name,
        "after_sale_type": type_name,
        "apply_time": after_sale.get("apply_time"),
        "elapsed_hours": round(elapsed, 1),
        "timeout_hours": timeout_hours,
        "reason": reason_text,
        "apply_amount": apply_amount,
        "recommended_action": recommended_action,
    }

    return {
        "customer_id": customer_id,
        "conversation_id": conversation_id,
        "product_id": after_sale_id,
        "product_name": f"售后 {after_sale_id}",
        "reason": reason,
        "suggested_copy": suggested_copy,
        "extra_json": extra_json,
        "priority": priority,
    }


def evaluate_conversation_for_recommendation(
    conversation_context: dict,
    conversation_id: int,
    customer_id: int,
    order_timeout_hours: int = DEFAULT_ORDER_TIMEOUT_HOURS,
    after_sale_timeout_hours: int = DEFAULT_AFTER_SALE_TIMEOUT_HOURS,
    now: Optional[datetime] = None,
) -> list[dict]:
    """
    Evaluate all recommendation rules against a conversation context
    and return a list of Recommendation payloads to be created.
    """
    recommendations = []
    orders = conversation_context.get("orders", [])
    if not orders:
        return recommendations

    first = orders[0]
    platform = first.get("platform")
    order_facts = first.get("order")
    shipment_facts = first.get("shipment")
    after_sales_facts = first.get("after_sales", [])
    inventory_facts = first.get("inventory")

    inv_recs = evaluate_inventory_shortage(
        order=order_facts,
        inventory=inventory_facts,
        conversation_id=conversation_id,
        customer_id=customer_id,
        platform=platform,
    )
    recommendations.extend(inv_recs)

    ship_rec = evaluate_shipment_pending_timeout(
        order=order_facts,
        shipment=shipment_facts,
        conversation_id=conversation_id,
        customer_id=customer_id,
        platform=platform,
        timeout_hours=order_timeout_hours,
        now=now,
    )
    if ship_rec:
        recommendations.append(ship_rec)

    for as_item in after_sales_facts[:3]:
        as_rec = evaluate_after_sale_processing_timeout(
            after_sale=as_item,
            conversation_id=conversation_id,
            customer_id=customer_id,
            platform=platform,
            timeout_hours=after_sale_timeout_hours,
            now=now,
        )
        if as_rec:
            recommendations.append(as_rec)

    return recommendations
