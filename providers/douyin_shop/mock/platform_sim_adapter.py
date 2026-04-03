"""
Adapter layer: platform-sim Query API format → mock-platform-server format.

platform-sim returns unified fixture data from user JSON files.
The mapper expects the old mock-platform-server flat format.
This adapter bridges the two for Douyin Shop.
"""


def adapt_platform_sim_order(order_data: dict) -> dict:
    """Convert platform-sim order format to mapper-expected format.

    platform-sim douyin_shop provider returns:
    - total_amount / pay_amount (not "amount")
    - products (not "items")
    - products[].product_id / num (not sku_id / quantity)
    - freight (not freight_amount)
    - receiver.name / phone / address
    """
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
                district = rest[city_end:]
            else:
                city = rest
        elif "市" in receiver_addr:
            city_end = receiver_addr.index("市") + 1
            city = receiver_addr[:city_end]
            rest = receiver_addr[city_end:]
            if "区" in rest:
                district_end = rest.index("区") + 1
                district = rest[:district_end]
                rest = rest[district_end:]
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

    return {
        "orderId": order_data.get("order_id", ""),
        "orderStatus": order_data.get("status", ""),
        "orderStatusName": order_data.get("status_text", ""),
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
