"""Adapter layer: platform-sim Query API format → mock-platform-server format for Kuaishou."""


def adapt_platform_sim_order(order_data: dict) -> dict:
    if not order_data:
        return {}

    receiver = order_data.get("receiver", {})
    receiver_addr = receiver.get("address", "")

    items = []
    for item in order_data.get("product_items", order_data.get("items", [])):
        items.append({
            "skuId": item.get("product_id", item.get("sku_id", "")),
            "skuName": item.get("name", item.get("sku_name", "")),
            "quantity": item.get("quantity", item.get("num", 0)),
            "price": float(item.get("price", 0)),
            "subTotal": float(item.get("price", 0)) * item.get("quantity", item.get("num", 0)),
        })

    total_amount = order_data.get("total_amount", order_data.get("amount", 0))
    pay_amount = order_data.get("pay_amount", order_data.get("amount", 0))

    status_code_map = {
        "created": "CREATED",
        "paid": "PAID",
        "wait_delivery": "WAIT_DELIVERY",
        "delivered": "DELIVERED",
        "finished": "FINISHED",
        "cancelled": "CANCELLED",
    }
    raw_status = order_data.get("status", "")
    ks_status = status_code_map.get(raw_status, raw_status)

    return {
        "orderId": order_data.get("order_id", ""),
        "orderStatus": ks_status,
        "orderStatusName": order_data.get("status_text", raw_status),
        "createTime": order_data.get("created_at"),
        "payTime": order_data.get("pay_time"),
        "totalAmount": float(total_amount) if total_amount else 0.0,
        "freightAmount": float(order_data.get("freight", 0)),
        "discountAmount": 0.0,
        "paymentAmount": float(pay_amount) if pay_amount else 0.0,
        "buyerNick": receiver.get("name", ""),
        "buyerPhone": receiver.get("phone", ""),
        "receiverName": receiver.get("name", ""),
        "receiverPhone": receiver.get("phone", ""),
        "receiverAddress": {
            "province": "",
            "city": "",
            "district": "",
            "detail": receiver_addr,
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

    company = shipment_data.get("company", shipment_data.get("logistics_company", ""))
    tracking = shipment_data.get("tracking_no", "")

    return {
        "orderId": order_id,
        "shipments": [
            {
                "shipmentId": tracking or shipment_data.get("shipment_id", ""),
                "expressCompany": company,
                "expressNo": tracking,
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
        "applied": "退款申请中",
        "processing": "退款审核中",
        "success": "退款成功",
        "rejected": "退款已拒绝",
    }
    refund_status = refund_data.get("status", "")
    return {
        "afterSaleId": refund_data.get("refund_id", f"REFUND_{order_id}"),
        "orderId": order_id,
        "type": refund_data.get("refund_type", "refund"),
        "typeName": "退款",
        "status": refund_status,
        "statusName": refund_status_map.get(refund_status, refund_data.get("status_text", refund_status)),
        "applyTime": refund_data.get("apply_time"),
        "handleTime": refund_data.get("audit_time"),
        "applyAmount": float(refund_data.get("refund_amount", refund_data.get("amount", 0))),
        "approveAmount": float(refund_data.get("refund_amount", refund_data.get("amount", 0))),
        "reason": refund_data.get("reason", ""),
        "reasonDetail": refund_data.get("reason", ""),
        "raw_json": refund_data,
    }


def adapt_platform_sim_inventory(inventory_data: list, order_id: str) -> dict:
    if not inventory_data:
        return {"orderId": order_id, "items": []}

    items = []
    for item in inventory_data:
        items.append({
            "productId": item.get("product_id", ""),
            "productName": item.get("product_name", ""),
            "stockNum": item.get("stock_num", 0),
            "status": item.get("status", 1),
        })

    return {
        "orderId": order_id,
        "items": items,
        "raw_json": inventory_data,
    }
