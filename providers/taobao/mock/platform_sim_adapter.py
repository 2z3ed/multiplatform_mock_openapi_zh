"""
Adapter layer: platform-sim Query API format → mock-platform-server format.
For Taobao platform.
"""


def adapt_platform_sim_order(order_data: dict) -> dict:
    if not order_data:
        return {}

    receiver = order_data.get("receiver", {})
    receiver_addr = receiver.get("address", "")
    parts = receiver_addr.split("区") if "区" in receiver_addr else receiver_addr.split("市")
    province = parts[0] if len(parts) > 1 else ""
    city = parts[1] if len(parts) > 1 else ""
    district = ""
    detail = receiver_addr

    items = []
    for item in order_data.get("items", []):
        items.append({
            "skuId": item.get("sku_id", ""),
            "skuName": item.get("name", ""),
            "quantity": item.get("quantity", 0),
            "price": float(item.get("price", 0)),
            "subTotal": float(item.get("price", 0)) * item.get("quantity", 1),
        })

    status_code_map = {
        "WAIT_BUYER_PAY": "WAIT_BUYER_PAY",
        "paid": "WAIT_SELLER_CONSIGN",
        "wait_ship": "WAIT_SELLER_CONSIGN",
        "WAIT_SELLER_SEND_GOODS": "WAIT_SELLER_CONSIGN",
        "shipped": "WAIT_BUYER_CONFIRM",
        "in_transit": "WAIT_BUYER_CONFIRM",
        "finished": "TRADE_FINISHED",
        "completed": "TRADE_FINISHED",
        "TRADE_FINISHED": "TRADE_FINISHED",
        "refunding": "TRADE_REFUNDING",
        "returned": "TRADE_REFUNDING",
    }
    status_text_map = {
        "WAIT_BUYER_PAY": "等待买家付款",
        "paid": "已付款待发货",
        "wait_ship": "已付款待发货",
        "WAIT_SELLER_SEND_GOODS": "已付款待发货",
        "shipped": "已发货",
        "in_transit": "运输中",
        "finished": "已完成",
        "completed": "已完成",
        "TRADE_FINISHED": "交易完成",
        "refunding": "退款中",
        "returned": "退货已签收",
    }
    raw_status = order_data.get("status", "")
    tb_status = status_code_map.get(raw_status, raw_status)
    tb_status_name = status_text_map.get(raw_status, order_data.get("status_text", ""))

    return {
        "orderId": order_data.get("order_id", ""),
        "orderStatus": tb_status,
        "orderStatusName": tb_status_name,
        "createTime": order_data.get("created_at"),
        "payTime": order_data.get("paid_at"),
        "totalAmount": float(order_data.get("amount", 0)),
        "freightAmount": 0.0,
        "discountAmount": 0.0,
        "paymentAmount": float(order_data.get("amount", 0)),
        "buyerNick": receiver.get("name", ""),
        "buyerPhone": receiver.get("phone", ""),
        "receiverName": receiver.get("name", ""),
        "receiverPhone": receiver.get("phone", ""),
        "receiverAddress": {
            "province": province,
            "city": city,
            "district": district,
            "detail": detail,
        } if receiver_addr else None,
        "items": items,
        "raw_json": order_data,
    }


def adapt_platform_sim_shipment(shipment_data: dict, order_id: str) -> dict:
    if not shipment_data:
        return {"orderId": order_id, "shipments": []}

    traces = []
    for node in shipment_data.get("nodes", []):
        traces.append({
            "time": node.get("time", ""),
            "message": node.get("node", ""),
            "location": "",
        })

    return {
        "orderId": order_id,
        "shipments": [
            {
                "shipmentId": shipment_data.get("tracking_no", ""),
                "expressCompany": shipment_data.get("company", ""),
                "expressNo": shipment_data.get("tracking_no", ""),
                "status": shipment_data.get("status", ""),
                "statusName": {
                    "in_transit": "运输中",
                    "delivered": "已签收",
                    "pending": "待发货",
                    "returned": "已退货",
                }.get(shipment_data.get("status", ""), shipment_data.get("status", "")),
                "createTime": traces[0]["time"] if traces else None,
                "estimatedArrival": None,
                "trace": traces,
            }
        ],
        "raw_json": shipment_data,
    }


def adapt_platform_sim_refund(refund_data: dict, order_id: str) -> dict:
    if not refund_data:
        return {"orderId": order_id}

    refund_status_map = {
        "refunding": "退款审核中",
        "refund_success": "退款成功",
        "refund_closed": "退款已关闭",
        "refund_requested": "退款申请中",
    }
    refund_status = refund_data.get("status", "")
    return {
        "afterSaleId": f"REFUND_{order_id}",
        "orderId": order_id,
        "type": "refund",
        "typeName": "退款",
        "status": refund_status,
        "statusName": refund_status_map.get(refund_status, refund_data.get("status_text", refund_status)),
        "applyTime": refund_data.get("apply_time"),
        "handleTime": refund_data.get("audit_time"),
        "applyAmount": float(refund_data.get("amount", 0)),
        "approveAmount": float(refund_data.get("amount", 0)),
        "reason": refund_data.get("reason", ""),
        "reasonDetail": refund_data.get("reason", ""),
        "raw_json": refund_data,
    }
