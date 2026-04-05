"""
Followup rule service: evaluates real business facts and auto-creates FollowupTasks.

Rules:
1. shipment_pending_timeout — order is "paid but not shipped" beyond threshold
2. after_sale_processing_timeout — after-sale is "processing" beyond threshold
"""
from datetime import datetime, timedelta, timezone
from typing import Optional


DEFAULT_ORDER_TIMEOUT_HOURS = 24
DEFAULT_AFTER_SALE_TIMEOUT_HOURS = 48


def _parse_time(value: Optional[str]) -> Optional[datetime]:
    """Parse an ISO time string into a naive datetime (treated as UTC)."""
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


def evaluate_shipment_pending_timeout(
    order: Optional[dict],
    conversation_id: int,
    customer_id: int,
    platform: Optional[str] = None,
    timeout_hours: int = DEFAULT_ORDER_TIMEOUT_HOURS,
    now: Optional[datetime] = None,
) -> Optional[dict]:
    """
    Rule 1: If order is in "paid but not shipped" state and exceeds timeout,
    return a FollowupTask payload to be created.
    """
    if not order:
        return None

    status = (order.get("status") or "").lower()
    pending_shipment_statuses = {
        "wait_seller_send_goods", "paid", "pending_shipment",
    }
    if status not in pending_shipment_statuses:
        return None

    external_order_id = order.get("order_id", "")
    if not external_order_id:
        return None

    pay_time = _parse_time(order.get("pay_time")) or _parse_time(order.get("create_time"))
    elapsed = _hours_since(pay_time, now)
    if elapsed is None or elapsed < timeout_hours:
        return None

    status_name = order.get("status_name", order.get("status", "未知"))
    total_amount = order.get("total_amount") or order.get("payment_amount", "")
    receiver_name = order.get("receiver_name", "")

    title = f"订单 {external_order_id} 超时未发货"
    description = (
        f"订单状态：{status_name}，"
        f"已等待约 {int(elapsed)} 小时（阈值 {timeout_hours}h）。"
    )
    if total_amount:
        description += f"订单金额：¥{total_amount}。"
    if receiver_name:
        description += f"收货人：{receiver_name}。"

    suggested_copy = (
        f"您好，您的订单 {external_order_id} 目前状态为「{status_name}」。"
        f"我们已为您跟进发货进度，预计尽快为您安排发出，请耐心等待。"
    )

    due_date = (now or datetime.utcnow()) + timedelta(hours=timeout_hours)

    return {
        "customer_id": customer_id,
        "conversation_id": conversation_id,
        "task_type": "shipment_pending_timeout",
        "trigger_source": "auto_rule",
        "title": title,
        "description": description,
        "suggested_copy": suggested_copy,
        "priority": "medium",
        "order_id": external_order_id,
        "due_date": due_date,
        "extra_json": {
            "platform": platform,
            "order_status": status,
            "order_status_name": status_name,
            "pay_time": order.get("pay_time"),
            "create_time": order.get("create_time"),
            "elapsed_hours": round(elapsed, 1),
            "timeout_hours": timeout_hours,
            "rule": "shipment_pending_timeout",
        },
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
    Rule 2: If after-sale is in "processing" state and exceeds timeout,
    return a FollowupTask payload to be created.
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
    reason = after_sale.get("reason", "")
    apply_amount = after_sale.get("apply_amount", "")

    title = f"售后 {after_sale_id} 超时未处理"
    description = (
        f"售后状态：{status_name}，"
        f"已等待约 {int(elapsed)} 小时（阈值 {timeout_hours}h）。"
    )
    if type_name:
        description += f"售后类型：{type_name}。"
    if apply_amount:
        description += f"申请金额：¥{apply_amount}。"
    if reason:
        description += f"申请原因：{reason}。"

    suggested_copy = (
        f"您好，关于您的售后申请 {after_sale_id}，"
        f"目前状态为「{status_name}」。我们已加急跟进，"
        f"预计尽快给您反馈，请耐心等待。"
    )

    due_date = (now or datetime.utcnow()) + timedelta(hours=timeout_hours)

    return {
        "customer_id": customer_id,
        "conversation_id": conversation_id,
        "task_type": "after_sale_processing_timeout",
        "trigger_source": "auto_rule",
        "title": title,
        "description": description,
        "suggested_copy": suggested_copy,
        "priority": "high",
        "order_id": order_id or None,
        "due_date": due_date,
        "extra_json": {
            "platform": platform,
            "after_sale_id": after_sale_id,
            "after_sale_status": status,
            "after_sale_status_name": status_name,
            "apply_time": after_sale.get("apply_time"),
            "elapsed_hours": round(elapsed, 1),
            "timeout_hours": timeout_hours,
            "rule": "after_sale_processing_timeout",
        },
    }


def evaluate_conversation_for_followup(
    conversation_context: dict,
    conversation_id: int,
    customer_id: int,
    order_timeout_hours: int = DEFAULT_ORDER_TIMEOUT_HOURS,
    after_sale_timeout_hours: int = DEFAULT_AFTER_SALE_TIMEOUT_HOURS,
    now: Optional[datetime] = None,
) -> list[dict]:
    """
    Evaluate all rules against a conversation context and return
    a list of FollowupTask payloads that should be created.
    """
    tasks = []
    orders = conversation_context.get("orders", [])
    if not orders:
        return tasks

    first = orders[0]
    platform = first.get("platform")
    order_facts = first.get("order")

    shipment_task = evaluate_shipment_pending_timeout(
        order=order_facts,
        conversation_id=conversation_id,
        customer_id=customer_id,
        platform=platform,
        timeout_hours=order_timeout_hours,
        now=now,
    )
    if shipment_task:
        tasks.append(shipment_task)

    after_sales_facts = first.get("after_sales", [])
    for as_item in after_sales_facts[:3]:
        as_task = evaluate_after_sale_processing_timeout(
            after_sale=as_item,
            conversation_id=conversation_id,
            customer_id=customer_id,
            platform=platform,
            timeout_hours=after_sale_timeout_hours,
            now=now,
        )
        if as_task:
            tasks.append(as_task)

    return tasks
