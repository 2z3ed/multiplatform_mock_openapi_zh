"""
Risk rule service: evaluates real business facts and auto-creates RiskFlags.

Rules:
1. frequent_after_sale — multiple after-sales or high refund risk
2. high_amount_order — order amount exceeds threshold
3. fulfillment_conflict — user wants exchange/resend but inventory is insufficient
"""
from datetime import datetime
from typing import Optional


DEFAULT_AMOUNT_THRESHOLD = 5000


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


def evaluate_frequent_after_sale(
    after_sales: list[dict],
    conversation_id: int,
    customer_id: int,
    platform: Optional[str] = None,
) -> Optional[dict]:
    """
    Rule 1: If there are multiple after-sales (>=2) or any with high amount,
    generate a frequent-after-sale risk flag.
    """
    if not after_sales:
        return None

    active_count = 0
    total_amount = 0
    reasons = []
    statuses = []

    for as_item in after_sales:
        status = (as_item.get("status") or "").lower()
        if status not in ("refunded", "success", "completed", "approved", "rejected", "closed", "cancelled"):
            active_count += 1
        statuses.append(as_item.get("status_name", as_item.get("status", "未知")))
        amount = as_item.get("apply_amount", 0) or 0
        total_amount += amount
        reason = as_item.get("reason", "")
        if reason:
            reasons.append(reason)

    if len(after_sales) < 2 and active_count == 0:
        return None

    after_sale_ids = ", ".join(a.get("after_sale_id", "") for a in after_sales[:3])
    reason_summary = "；".join(reasons[:3]) if reasons else "无"

    if len(after_sales) >= 3 or total_amount >= 2000:
        risk_level = "high"
    elif len(after_sales) >= 2 or active_count >= 1:
        risk_level = "medium"
    else:
        risk_level = "low"

    description = (
        f"该客户关联 {len(after_sales)} 条售后记录（{active_count} 条处理中），"
        f"累计申请金额 ¥{total_amount}。"
        f"售后状态：{', '.join(statuses)}。"
    )
    if reason_summary != "无":
        description += f"申请原因：{reason_summary}。"

    return {
        "customer_id": customer_id,
        "conversation_id": conversation_id,
        "risk_type": "frequent_after_sale",
        "risk_level": risk_level,
        "description": description,
        "extra_json": {
            "platform": platform,
            "rule": "frequent_after_sale",
            "after_sale_count": len(after_sales),
            "active_after_sale_count": active_count,
            "total_apply_amount": total_amount,
            "after_sale_ids": after_sale_ids,
            "statuses": statuses,
            "reasons": reasons,
        },
    }


def evaluate_high_amount_order(
    order: Optional[dict],
    conversation_id: int,
    customer_id: int,
    platform: Optional[str] = None,
    amount_threshold: int = DEFAULT_AMOUNT_THRESHOLD,
) -> Optional[dict]:
    """
    Rule 2: If order total_amount exceeds threshold, generate a high-amount risk flag.
    """
    if not order:
        return None

    total_amount = order.get("total_amount") or order.get("payment_amount", 0)
    try:
        total_amount = float(total_amount) if total_amount else 0
    except (ValueError, TypeError):
        total_amount = 0
    if total_amount < amount_threshold:
        return None

    order_id = order.get("order_id", "")
    status_name = order.get("status_name", order.get("status", "未知"))

    if total_amount >= amount_threshold * 2:
        risk_level = "high"
    else:
        risk_level = "medium"

    description = (
        f"订单 {order_id} 金额 ¥{total_amount} 超过预警阈值（¥{amount_threshold}），"
        f"当前状态：{status_name}。"
    )

    return {
        "customer_id": customer_id,
        "conversation_id": conversation_id,
        "risk_type": "high_amount_order",
        "risk_level": risk_level,
        "description": description,
        "extra_json": {
            "platform": platform,
            "rule": "high_amount_order",
            "order_id": order_id,
            "order_status": order.get("status"),
            "order_status_name": status_name,
            "total_amount": total_amount,
            "amount_threshold": amount_threshold,
        },
    }


def evaluate_fulfillment_conflict(
    order: Optional[dict],
    inventory: Optional[dict],
    conversation_id: int,
    customer_id: int,
    platform: Optional[str] = None,
) -> list[dict]:
    """
    Rule 3: If inventory has out_of_stock or low_stock items and order is in a state
    where resend/exchange might be requested, generate fulfillment conflict risk flags.
    """
    flags = []
    if not inventory or not inventory.get("items"):
        return flags

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
            risk_level = "high"
            description = (
                f"{product_name} 当前缺货（库存 {quantity} 件），"
                f"若客户提出补发/换货需求，将无法正常履约。"
            )
        else:
            risk_level = "medium"
            description = (
                f"{product_name} 库存紧张（仅剩 {quantity} 件），"
                f"若客户提出补发/换货需求，可能无法满足。"
            )

        extra_json = {
            "platform": platform,
            "rule": "fulfillment_conflict",
            "sku_id": sku_id,
            "product_name": product_name,
            "stock_state": stock_state,
            "quantity": quantity,
            "warehouse_name": warehouse_name,
            "order_status": order_status,
        }

        flags.append({
            "customer_id": customer_id,
            "conversation_id": conversation_id,
            "risk_type": "fulfillment_conflict",
            "risk_level": risk_level,
            "description": description,
            "extra_json": extra_json,
        })

    return flags


def evaluate_conversation_for_risk(
    conversation_context: dict,
    conversation_id: int,
    customer_id: int,
    amount_threshold: int = DEFAULT_AMOUNT_THRESHOLD,
) -> list[dict]:
    """
    Evaluate all risk rules against a conversation context
    and return a list of RiskFlag payloads to be created.
    """
    flags = []
    orders = conversation_context.get("orders", [])
    if not orders:
        return flags

    first = orders[0]
    platform = first.get("platform")
    order_facts = first.get("order")
    after_sales_facts = first.get("after_sales", [])
    inventory_facts = first.get("inventory")

    as_flag = evaluate_frequent_after_sale(
        after_sales=after_sales_facts,
        conversation_id=conversation_id,
        customer_id=customer_id,
        platform=platform,
    )
    if as_flag:
        flags.append(as_flag)

    amount_flag = evaluate_high_amount_order(
        order=order_facts,
        conversation_id=conversation_id,
        customer_id=customer_id,
        platform=platform,
        amount_threshold=amount_threshold,
    )
    if amount_flag:
        flags.append(amount_flag)

    fulfillment_flags = evaluate_fulfillment_conflict(
        order=order_facts,
        inventory=inventory_facts,
        conversation_id=conversation_id,
        customer_id=customer_id,
        platform=platform,
    )
    flags.extend(fulfillment_flags)

    return flags
