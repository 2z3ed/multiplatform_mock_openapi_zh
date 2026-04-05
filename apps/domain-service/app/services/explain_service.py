"""
Explain service: converts real business facts into customer-service-readable explanations.

Each explainer takes normalized fact dicts (from context aggregation) and returns
a structured explanation with source_summary that can be consumed by AI suggest-reply
or displayed in the frontend.
"""
from typing import Optional


def _explain_order_status(status: str, status_name: str) -> str:
    """Map raw order status to a human-readable explanation."""
    status_lower = (status or "").lower()
    name = status_name or status or "未知"

    if status_lower in ("wait_buyer_pay", "pending_payment", "created"):
        return f"订单当前状态为「{name}」，客户尚未完成付款。"
    elif status_lower in ("wait_seller_send_goods", "paid", "pending_shipment"):
        return f"订单当前状态为「{name}」，已付款等待发货。"
    elif status_lower in ("seller_consignment", "shipped", "in_transit"):
        return f"订单当前状态为「{name}」，商品已发出，正在运输中。"
    elif status_lower in ("buyer_confirm_received", "delivered"):
        return f"订单当前状态为「{name}」，物流显示已送达，等待客户确认收货。"
    elif status_lower in ("trade_success", "completed", "finished"):
        return f"订单当前状态为「{name}」，交易已完成。"
    elif status_lower in ("trade_closed", "closed", "cancelled"):
        return f"订单当前状态为「{name}」，订单已关闭或取消。"
    else:
        return f"订单当前状态为「{name}」。"


def explain_order(order: dict) -> dict:
    """Explain order status based on real order facts."""
    if not order:
        return {
            "type": "order",
            "status_label": "无订单信息",
            "explanation": "当前会话未关联到订单信息。",
            "source_summary": "",
        }

    status = order.get("status", "")
    status_name = order.get("status_name", status or "未知")
    order_id = order.get("order_id", "")
    total_amount = order.get("total_amount") or order.get("payment_amount", "")
    items = order.get("items", [])
    receiver_name = order.get("receiver_name", "")
    create_time = order.get("create_time", "")
    pay_time = order.get("pay_time", "")

    explanation = _explain_order_status(status, status_name)

    parts = [explanation]
    if order_id:
        parts.append(f"订单号：{order_id}")
    if total_amount:
        parts.append(f"订单金额：¥{total_amount}")
    if receiver_name:
        parts.append(f"收货人：{receiver_name}")
    if items:
        item_summary = ", ".join(
            f"{i.get('sku_name', '')}x{i.get('quantity', 0)}"
            for i in items[:3]
        )
        if item_summary:
            parts.append(f"商品：{item_summary}")

    source_summary = "，".join(parts)

    suggestion = ""
    status_lower = (status or "").lower()
    if status_lower in ("wait_buyer_pay", "pending_payment", "created"):
        suggestion = "可提醒客户尽快完成付款。"
    elif status_lower in ("wait_seller_send_goods", "paid", "pending_shipment"):
        suggestion = "可告知客户预计发货时间，或协助催发货。"
    elif status_lower in ("seller_consignment", "shipped", "in_transit"):
        suggestion = "可提供物流单号，或协助查询最新物流状态。"
    elif status_lower in ("trade_success", "completed", "finished"):
        suggestion = "可询问客户是否满意，或引导评价。"

    return {
        "type": "order",
        "status_label": status_name,
        "explanation": explanation,
        "source_summary": source_summary,
        "suggestion": suggestion,
    }


def explain_shipment(shipment: dict) -> dict:
    """Explain shipment status based on real shipment facts."""
    if not shipment:
        return {
            "type": "shipment",
            "status_label": "无物流信息",
            "explanation": "当前暂无物流信息。",
            "source_summary": "",
        }

    shipments = shipment.get("shipments", [])
    if not shipments:
        return {
            "type": "shipment",
            "status_label": "无物流信息",
            "explanation": "订单尚未产生物流信息，可能还未发货。",
            "source_summary": "",
        }

    s = shipments[0]
    express_company = s.get("express_company", "")
    express_no = s.get("express_no", "")
    status = s.get("status", "")
    status_name = s.get("status_name", status or "未知")
    trace = s.get("trace", [])

    status_lower = (status or "").lower()

    if status_lower in ("no_tracking", "pending", "created"):
        explanation = f"物流状态为「{status_name}」，尚未有物流轨迹。"
    elif status_lower in ("accepted", "shipped", "in_transit", "transport"):
        explanation = f"物流状态为「{status_name}」，包裹正在运输中。"
    elif status_lower in ("delivered", "signed", "received"):
        explanation = f"物流状态为「{status_name}」，包裹已送达。"
    elif status_lower in ("exception", "abnormal", "delayed", "returned"):
        explanation = f"物流状态为「{status_name}」，物流可能存在异常。"
    else:
        explanation = f"物流状态为「{status_name}」。"

    parts = [explanation]
    if express_company:
        parts.append(f"快递公司：{express_company}")
    if express_no:
        parts.append(f"运单号：{express_no}")
    if trace:
        latest = trace[0]
        trace_msg = latest.get("message", "")
        trace_time = latest.get("time", "")
        if trace_msg:
            parts.append(f"最新物流：{trace_msg}")
        if trace_time:
            parts.append(f"物流时间：{trace_time}")

    source_summary = "，".join(parts)

    suggestion = ""
    if status_lower in ("no_tracking", "pending", "created"):
        suggestion = "可告知客户尚未发货，或协助催发货。"
    elif status_lower in ("accepted", "shipped", "in_transit", "transport"):
        suggestion = "可提供最新物流轨迹，或安抚客户耐心等待。"
    elif status_lower in ("delivered", "signed", "received"):
        suggestion = "可确认客户是否已收到货，或引导确认收货。"
    elif status_lower in ("exception", "abnormal", "delayed", "returned"):
        suggestion = "建议安抚客户，并协助联系物流核实情况。"

    return {
        "type": "shipment",
        "status_label": status_name,
        "explanation": explanation,
        "source_summary": source_summary,
        "suggestion": suggestion,
    }


def explain_after_sale(after_sale: dict) -> dict:
    """Explain after-sale status based on real after-sale facts."""
    if not after_sale:
        return {
            "type": "after_sale",
            "status_label": "无售后信息",
            "explanation": "当前暂无售后信息。",
            "source_summary": "",
            "suggestion": "",
        }

    status = after_sale.get("status", "")
    status_name = after_sale.get("status_name", status or "未知")
    type_name = after_sale.get("type_name", "")
    reason = after_sale.get("reason", "")
    apply_amount = after_sale.get("apply_amount", "")
    approve_amount = after_sale.get("approve_amount", "")
    after_sale_id = after_sale.get("after_sale_id", "")

    status_lower = (status or "").lower()

    if status_lower in ("apply", "pending", "waiting_for_seller"):
        explanation = f"售后状态为「{status_name}」，客户已提交售后申请，等待审核。"
    elif status_lower in ("processing", "under_review", "in_progress"):
        explanation = f"售后状态为「{status_name}」，售后正在处理中。"
    elif status_lower in ("refunded", "success", "completed", "approved"):
        explanation = f"售后状态为「{status_name}」，售后已完成。"
    elif status_lower in ("rejected", "closed", "cancelled"):
        explanation = f"售后状态为「{status_name}」，售后已被拒绝或取消。"
    else:
        explanation = f"售后状态为「{status_name}」。"

    parts = [explanation]
    if type_name:
        parts.append(f"售后类型：{type_name}")
    if apply_amount:
        parts.append(f"申请金额：¥{apply_amount}")
    if approve_amount:
        parts.append(f"审核金额：¥{approve_amount}")
    if reason:
        parts.append(f"申请原因：{reason}")
    if after_sale_id:
        parts.append(f"售后单号：{after_sale_id}")

    source_summary = "，".join(parts)

    suggestion = ""
    if status_lower in ("apply", "pending", "waiting_for_seller"):
        suggestion = "可告知客户预计审核时间，或协助加快审核进度。"
    elif status_lower in ("processing", "under_review", "in_progress"):
        suggestion = "可安抚客户耐心等待，或协助跟进处理进度。"
    elif status_lower in ("refunded", "success", "completed", "approved"):
        suggestion = "可告知退款到账时间，或引导客户确认。"
    elif status_lower in ("rejected", "closed", "cancelled"):
        suggestion = "可解释拒绝原因，或引导客户重新提交售后申请。"

    return {
        "type": "after_sale",
        "status_label": status_name,
        "explanation": explanation,
        "source_summary": source_summary,
        "suggestion": suggestion,
    }


def explain_inventory(inventory: dict) -> dict:
    """Explain inventory status based on real inventory facts."""
    if not inventory:
        return {
            "type": "inventory",
            "status_label": "无库存信息",
            "explanation": "当前暂无库存信息。",
            "source_summary": "",
        }

    items = inventory.get("items", [])
    if not items:
        return {
            "type": "inventory",
            "status_label": "无库存信息",
            "explanation": "当前暂无可确认的库存信息。",
            "source_summary": "",
        }

    parts = []
    has_stock_items = []
    low_stock_items = []
    out_of_stock_items = []

    for item in items[:5]:
        stock_state = item.get("stock_state", "")
        quantity = item.get("quantity", 0)
        product_name = item.get("product_name", item.get("sku_id", ""))
        warehouse_name = item.get("warehouse_name", "")

        stock_lower = (stock_state or "").lower()
        if stock_lower in ("in_stock", "normal", "available"):
            label = "有货"
            has_stock_items.append(product_name)
        elif stock_lower in ("low_stock", "low", "warning"):
            label = "库存紧张"
            low_stock_items.append(product_name)
        elif stock_lower in ("out_of_stock", "out", "unavailable"):
            label = "无货"
            out_of_stock_items.append(product_name)
        else:
            label = stock_state or "未知"

        item_parts = [f"{product_name}：{label}"]
        if quantity is not None:
            item_parts.append(f"数量 {quantity} 件")
        if warehouse_name:
            item_parts.append(f"仓库：{warehouse_name}")
        parts.append("，".join(item_parts))

    explanation = "库存信息：" + "；".join(parts)

    source_summary = explanation

    suggestion = ""
    if out_of_stock_items:
        suggestion = f"{', '.join(out_of_stock_items)} 当前缺货，建议推荐替代商品或告知预计补货时间。"
    elif low_stock_items:
        suggestion = f"{', '.join(low_stock_items)} 库存紧张，建议提醒客户尽快下单。"
    elif has_stock_items:
        suggestion = "库存充足，可正常告知客户发货安排。"

    return {
        "type": "inventory",
        "status_label": "有货" if has_stock_items and not low_stock_items and not out_of_stock_items else ("库存紧张" if low_stock_items else ("缺货" if out_of_stock_items else "混合")),
        "explanation": explanation,
        "source_summary": source_summary,
        "suggestion": suggestion,
    }


def explain_from_context(conversation_context: dict) -> dict:
    """
    Generate explanations for all facts in a conversation context.

    Takes the output of aggregate_conversation_context and returns
    a dict with explanations for order, shipment, after_sale, and inventory.

    Returns:
    {
        "order": { type, status_label, explanation, source_summary, suggestion },
        "shipment": { ... },
        "after_sales": [ { ... }, ... ],
        "inventory": { ... },
        "formatted": "combined human-readable summary",
    }
    """
    orders = conversation_context.get("orders", [])
    if not orders:
        return {
            "order": explain_order(None),
            "shipment": explain_shipment(None),
            "after_sales": [explain_after_sale(None)],
            "inventory": explain_inventory(None),
            "formatted": "当前会话未关联到业务数据。",
        }

    first = orders[0]
    order_facts = first.get("order")
    shipment_facts = first.get("shipment")
    after_sales_facts = first.get("after_sales", [])
    inventory_facts = first.get("inventory")

    order_exp = explain_order(order_facts)
    shipment_exp = explain_shipment(shipment_facts)

    after_sales_exps = []
    if after_sales_facts:
        for as_item in after_sales_facts[:2]:
            after_sales_exps.append(explain_after_sale(as_item))
    else:
        after_sales_exps = [explain_after_sale(None)]

    inventory_exp = explain_inventory(inventory_facts)

    formatted_parts = []
    if order_exp.get("source_summary"):
        formatted_parts.append(order_exp["source_summary"])
    if shipment_exp.get("source_summary"):
        formatted_parts.append(shipment_exp["source_summary"])
    for as_exp in after_sales_exps:
        if as_exp.get("source_summary"):
            formatted_parts.append(as_exp["source_summary"])
    if inventory_exp.get("source_summary"):
        formatted_parts.append(inventory_exp["source_summary"])

    formatted = "；".join(formatted_parts) if formatted_parts else "当前暂无可确认的业务信息。"

    return {
        "order": order_exp,
        "shipment": shipment_exp,
        "after_sales": after_sales_exps,
        "inventory": inventory_exp,
        "formatted": formatted,
    }
