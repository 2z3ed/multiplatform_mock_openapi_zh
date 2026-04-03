"""
Adapter layer: platform-sim Query API format → mock-platform-server format.
For Taobao platform.
"""


def adapt_platform_sim_order(order_data: dict) -> dict:
    if not order_data:
        return {}

    receiver = order_data.get("receiver", {})
    receiver_addr = receiver.get("address", "")
    province = ""
    city = ""
    district = ""
    detail = receiver_addr

    if receiver_addr:
        if "省" in receiver_addr:
            province_end = receiver_addr.index("省") + 1
            province = receiver_addr[:province_end]
            rest = receiver_addr[province_end:]
            if "市" in rest:
                city_end = rest.index("市") + 1
                city = rest[:city_end]
                rest2 = rest[city_end:]
                if "区" in rest2:
                    district_end = rest2.index("区") + 1
                    district = rest2[:district_end]
                    detail = rest2[district_end:]
                else:
                    detail = rest2
            else:
                city = rest
        elif "市" in receiver_addr:
            city_end = receiver_addr.index("市") + 1
            city = receiver_addr[:city_end]
            rest = receiver_addr[city_end:]
            if "区" in rest:
                district_end = rest.index("区") + 1
                district = rest[:district_end]
                detail = rest[district_end:]
            else:
                detail = rest if rest else detail
        elif "区" in receiver_addr:
            district_end = receiver_addr.index("区") + 1
            district = receiver_addr[:district_end]

    items = []
    products = order_data.get("products", order_data.get("items", []))
    for item in products:
        product_id = item.get("product_id", item.get("sku_id", ""))
        name = item.get("name", item.get("sku_name", ""))
        quantity = item.get("num", item.get("quantity", 0))
        price = float(item.get("price", 0))
        items.append({
            "skuId": product_id,
            "skuName": name,
            "quantity": quantity,
            "price": price,
            "subTotal": price * quantity,
        })

    total_amount = order_data.get("total_amount", order_data.get("amount", 0))
    pay_amount = order_data.get("pay_amount", order_data.get("amount", 0))
    freight = order_data.get("freight", order_data.get("freight_amount", 0))

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
        "createTime": order_data.get("create_time", order_data.get("created_at")),
        "payTime": order_data.get("pay_time", order_data.get("paid_at")),
        "totalAmount": float(total_amount) if total_amount else 0.0,
        "freightAmount": float(freight) if freight else 0.0,
        "discountAmount": float(order_data.get("discount_amount", 0)),
        "paymentAmount": float(pay_amount) if pay_amount else 0.0,
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
