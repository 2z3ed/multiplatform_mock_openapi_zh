from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api", tags=["context"])

PROVIDER_MAP = {}


def _get_provider(platform: str):
    if platform == "jd":
        from providers.jd.mock.provider import JdMockProvider
        if "jd" not in PROVIDER_MAP:
            PROVIDER_MAP["jd"] = JdMockProvider()
        return PROVIDER_MAP["jd"]
    elif platform == "taobao":
        from providers.taobao.mock.provider import TaobaoMockProvider
        if "taobao" not in PROVIDER_MAP:
            PROVIDER_MAP["taobao"] = TaobaoMockProvider()
        return PROVIDER_MAP["taobao"]
    elif platform == "douyin_shop":
        from providers.douyin_shop.mock.provider import DouyinShopMockProvider
        if "douyin_shop" not in PROVIDER_MAP:
            PROVIDER_MAP["douyin_shop"] = DouyinShopMockProvider()
        return PROVIDER_MAP["douyin_shop"]
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown platform: {platform}")


@router.get("/orders/{platform}/{order_id}")
def get_order(platform: str, order_id: str) -> dict:
    provider = _get_provider(platform)
    order_dto = provider.get_order(order_id)
    return {
        "platform": order_dto.platform,
        "order_id": order_dto.order_id,
        "status": order_dto.status,
        "status_name": order_dto.status_name,
        "create_time": order_dto.create_time,
        "pay_time": order_dto.pay_time,
        "total_amount": order_dto.total_amount,
        "freight_amount": order_dto.freight_amount,
        "discount_amount": order_dto.discount_amount,
        "payment_amount": order_dto.payment_amount,
        "buyer_nick": order_dto.buyer_nick,
        "buyer_phone": order_dto.buyer_phone,
        "receiver_name": order_dto.receiver_name,
        "receiver_phone": order_dto.receiver_phone,
        "receiver_address": {
            "province": order_dto.receiver_address.province if order_dto.receiver_address else None,
            "city": order_dto.receiver_address.city if order_dto.receiver_address else None,
            "district": order_dto.receiver_address.district if order_dto.receiver_address else None,
            "detail": order_dto.receiver_address.detail if order_dto.receiver_address else None,
        } if order_dto.receiver_address else None,
        "items": [
            {
                "sku_id": item.sku_id,
                "sku_name": item.sku_name,
                "quantity": item.quantity,
                "price": item.price,
                "sub_total": item.sub_total
            }
            for item in order_dto.items
        ]
    }


@router.get("/shipments/{platform}/{order_id}")
def get_shipment(platform: str, order_id: str) -> dict:
    provider = _get_provider(platform)
    shipment_dto = provider.get_shipment(order_id)
    return {
        "platform": shipment_dto.platform,
        "order_id": shipment_dto.order_id,
        "shipments": [
            {
                "shipment_id": ship.shipment_id,
                "express_company": ship.express_company,
                "express_no": ship.express_no,
                "status": ship.status,
                "status_name": ship.status_name,
                "create_time": ship.create_time,
                "estimated_arrival": ship.estimated_arrival,
                "trace": [
                    {
                        "time": t.time,
                        "message": t.message,
                        "location": t.location
                    }
                    for t in ship.trace
                ]
            }
            for ship in shipment_dto.shipments
        ]
    }


@router.get("/after-sales/{platform}/{after_sale_id}")
def get_after_sale(platform: str, after_sale_id: str) -> dict:
    provider = _get_provider(platform)
    after_sale_dto = provider.get_after_sale(after_sale_id)
    return {
        "platform": after_sale_dto.platform,
        "after_sale_id": after_sale_dto.after_sale_id,
        "order_id": after_sale_dto.order_id,
        "type": after_sale_dto.type,
        "type_name": after_sale_dto.type_name,
        "status": after_sale_dto.status,
        "status_name": after_sale_dto.status_name,
        "apply_time": after_sale_dto.apply_time,
        "handle_time": after_sale_dto.handle_time,
        "apply_amount": after_sale_dto.apply_amount,
        "approve_amount": after_sale_dto.approve_amount,
        "reason": after_sale_dto.reason,
        "reason_detail": after_sale_dto.reason_detail
    }