from provider_sdk.dto.order_dto import OrderDTO, OrderItemDTO, AddressDTO
from provider_sdk.dto.shipment_dto import ShipmentDTO, ShipmentItemDTO, ShipmentTraceDTO
from provider_sdk.dto.after_sale_dto import AfterSaleDTO


def map_order(data: dict, platform: str) -> OrderDTO:
    address = None
    if "receiverAddress" in data and data["receiverAddress"]:
        addr = data["receiverAddress"]
        address = AddressDTO(
            province=addr.get("province", ""),
            city=addr.get("city", ""),
            district=addr.get("district", ""),
            detail=addr.get("detail", "")
        )

    items = []
    for item in data.get("items", []):
        items.append(OrderItemDTO(
            sku_id=item.get("skuId", ""),
            sku_name=item.get("skuName", ""),
            quantity=item.get("quantity", 0),
            price=item.get("price", 0.0),
            sub_total=item.get("subTotal", 0.0)
        ))

    return OrderDTO(
        platform=platform,
        order_id=data.get("orderId", ""),
        status=data.get("orderStatus", ""),
        status_name=data.get("orderStatusName", ""),
        create_time=data.get("createTime"),
        pay_time=data.get("payTime"),
        total_amount=data.get("totalAmount", 0.0),
        freight_amount=data.get("freightAmount", 0.0),
        discount_amount=data.get("discountAmount", 0.0),
        payment_amount=data.get("paymentAmount", 0.0),
        buyer_nick=data.get("buyerNick"),
        buyer_phone=data.get("buyerPhone"),
        receiver_name=data.get("receiverName"),
        receiver_phone=data.get("receiverPhone"),
        receiver_address=address,
        items=items,
        raw_json=data.get("raw_json", {})
    )


def map_shipment(data: dict, platform: str) -> ShipmentDTO:
    shipment_items = []
    for ship in data.get("shipments", []):
        traces = []
        for trace in ship.get("trace", []):
            traces.append(ShipmentTraceDTO(
                time=trace.get("time", ""),
                message=trace.get("message", ""),
                location=trace.get("location", "")
            ))
        shipment_items.append(ShipmentItemDTO(
            shipment_id=ship.get("shipmentId", ""),
            express_company=ship.get("expressCompany", ""),
            express_no=ship.get("expressNo", ""),
            status=ship.get("status", ""),
            status_name=ship.get("statusName", ""),
            create_time=ship.get("createTime"),
            estimated_arrival=ship.get("estimatedArrival"),
            trace=traces
        ))
    return ShipmentDTO(
        platform=platform,
        order_id=data.get("orderId", ""),
        shipments=shipment_items,
        raw_json=data.get("raw_json", {})
    )


def map_after_sale(data: dict, platform: str) -> AfterSaleDTO:
    return AfterSaleDTO(
        platform=platform,
        after_sale_id=data.get("afterSaleId", ""),
        order_id=data.get("orderId", ""),
        type=data.get("type", ""),
        type_name=data.get("typeName", ""),
        status=data.get("status", ""),
        status_name=data.get("statusName", ""),
        apply_time=data.get("applyTime"),
        handle_time=data.get("handleTime"),
        apply_amount=data.get("applyAmount", 0.0),
        approve_amount=data.get("approveAmount", 0.0),
        reason=data.get("reason"),
        reason_detail=data.get("reasonDetail"),
        raw_json=data.get("raw_json", {})
    )
