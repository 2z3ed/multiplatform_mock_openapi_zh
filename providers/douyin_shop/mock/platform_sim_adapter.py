"""
Adapter layer: platform-sim Query API format → mock-platform-server format.

platform-sim returns unified fixture data from user JSON files.
The mapper expects the old mock-platform-server flat format.
This adapter bridges the two for Douyin Shop.
"""


def adapt_platform_sim_order(order_data: dict) -> dict:
    """Convert platform-sim order format to mapper-expected format."""
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

    return {
        "orderId": order_data.get("order_id", ""),
        "orderStatus": order_data.get("status", ""),
        "orderStatusName": order_data.get("status_text", ""),
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
    """Convert platform-sim shipment format to mapper-expected format."""
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
    """Convert platform-sim refund format to mapper-expected format."""
    if not refund_data:
        return {"orderId": order_id}

    return {
        "refundId": f"REFUND_{order_id}",
        "orderId": order_id,
        "type": "refund",
        "typeName": "退款",
        "status": refund_data.get("status", ""),
        "statusName": refund_data.get("status", ""),
        "applyTime": refund_data.get("apply_time"),
        "handleTime": refund_data.get("audit_time"),
        "applyAmount": float(refund_data.get("amount", 0)),
        "approveAmount": float(refund_data.get("amount", 0)),
        "reason": refund_data.get("reason", ""),
        "reasonDetail": refund_data.get("reason", ""),
        "raw_json": refund_data,
    }
