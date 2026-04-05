from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from shared_db import get_db

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
    elif platform == "wecom_kf":
        from providers.wecom_kf.mock.provider import WecomKfMockProvider
        if "wecom_kf" not in PROVIDER_MAP:
            PROVIDER_MAP["wecom_kf"] = WecomKfMockProvider()
        return PROVIDER_MAP["wecom_kf"]
    elif platform == "kuaishou":
        from providers.kuaishou.mock.provider import KuaishouMockProvider
        if "kuaishou" not in PROVIDER_MAP:
            PROVIDER_MAP["kuaishou"] = KuaishouMockProvider()
        return PROVIDER_MAP["kuaishou"]
    elif platform == "xhs":
        from providers.xhs.mock.provider import XhsMockProvider
        if "xhs" not in PROVIDER_MAP:
            PROVIDER_MAP["xhs"] = XhsMockProvider()
        return PROVIDER_MAP["xhs"]
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


@router.get("/inventory/{platform}/{order_id}")
def get_inventory(platform: str, order_id: str) -> dict:
    provider = _get_provider(platform)
    inventory_dto = provider.get_inventory(order_id)
    return {
        "platform": inventory_dto.platform,
        "order_id": inventory_dto.order_id,
        "items": [
            {
                "sku_id": item.sku_id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "stock_state": item.stock_state,
                "quantity": item.quantity,
                "warehouse_name": item.warehouse_name,
            }
            for item in inventory_dto.items
        ]
    }


@router.get("/orders/resolve")
def resolve_order(
    platform: str = Query(...),
    external_order_id: str = Query(...),
    account_id: str = Query(""),
    source_system: str = Query("platform"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Resolve an external platform order ID to the internal order_core.id.
    Returns the internal order ID plus all known external identities for that order.
    """
    from app.services.identity_service import (
        resolve_order_id as _resolve_order_id,
        list_conversation_ids_for_order as _list_convos,
    )
    from app.repositories.order_identity_repository import get_by_order_id as _get_identities
    from app.repositories.order_core_repository import get_by_id as _get_order

    internal_order_id = _resolve_order_id(db, source_system, platform, external_order_id, account_id)
    if internal_order_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No internal order found for platform={platform}, external_order_id={external_order_id}",
        )

    order = _get_order(db, internal_order_id)
    identities = _get_identities(db, internal_order_id)
    conversations = _list_convos(db, internal_order_id)

    return {
        "internal_order_id": internal_order_id,
        "customer_id": order.customer_id if order else None,
        "current_status": order.current_status if order else None,
        "total_amount": order.total_amount if order else None,
        "currency": order.currency if order else None,
        "identities": [
            {
                "source_system": i.source_system,
                "platform": i.platform,
                "account_id": i.account_id,
                "external_order_id": i.external_order_id,
                "external_status": i.external_status,
                "is_primary": i.is_primary,
            }
            for i in identities
        ],
        "linked_conversations": conversations,
    }


@router.get("/shipments/resolve")
def resolve_shipment(
    platform: str = Query(...),
    external_order_id: str = Query(...),
    account_id: str = Query(""),
    source_system: str = Query("platform"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Resolve shipment data through the unified order identity layer.

    Chain:
      external_order_id -> resolve_order_id -> order_core.id
      -> order_identity_mapping -> shipment_snapshot lookup
      -> existing provider for live shipment data

    This proves shipment queries can go through the internal order key
    instead of directly using external order IDs.
    """
    from app.services.identity_service import resolve_order_id as _resolve_order_id
    from app.repositories.order_identity_repository import get_by_order_id as _get_identities
    from app.repositories.order_core_repository import get_by_id as _get_order
    from domain_models.models.shipment_snapshot import ShipmentSnapshot

    internal_order_id = _resolve_order_id(db, source_system, platform, external_order_id, account_id)
    if internal_order_id is None:
        internal_order_id = _resolve_order_id(db, platform, platform, external_order_id, account_id)
    if internal_order_id is None:
        internal_order_id = _resolve_order_id(db, "odoo", platform, external_order_id, account_id)
    if internal_order_id is None:
        internal_order_id = _resolve_order_id(db, "odoo", "odoo", external_order_id, "demo")
    if internal_order_id is None:
        return {
            "internal_order_id": None,
            "resolved": False,
            "shipment_from_snapshot": None,
            "shipment_from_provider": None,
        }

    order = _get_order(db, internal_order_id)
    identities = _get_identities(db, internal_order_id)

    shipment_from_snapshot = None
    for identity in identities:
        snaps = db.query(ShipmentSnapshot).filter_by(
            platform=identity.platform,
            order_id=identity.external_order_id,
        ).all()
        if snaps:
            shipment_from_snapshot = {
                "id": snaps[0].id,
                "platform": snaps[0].platform,
                "order_id": snaps[0].order_id,
                "shipment_status": snaps[0].shipment_status,
                "tracking_no": snaps[0].tracking_no,
                "carrier": snaps[0].carrier,
            }
            break

    shipment_from_provider = None
    try:
        provider = _get_provider(platform)
        dto = provider.get_shipment(external_order_id)
        shipment_from_provider = {
            "platform": dto.platform,
            "order_id": dto.order_id,
            "shipment_count": len(dto.shipments),
            "shipments": [
                {
                    "shipment_id": s.shipment_id,
                    "express_company": s.express_company,
                    "express_no": s.express_no,
                    "status": s.status,
                    "status_name": s.status_name,
                }
                for s in dto.shipments
            ],
        }
    except Exception as e:
        shipment_from_provider = {"error": str(e)}

    return {
        "internal_order_id": internal_order_id,
        "resolved": True,
        "customer_id": order.customer_id if order else None,
        "current_status": order.current_status if order else None,
        "identities": [
            {
                "source_system": i.source_system,
                "platform": i.platform,
                "account_id": i.account_id,
                "external_order_id": i.external_order_id,
                "external_status": i.external_status,
                "is_primary": i.is_primary,
            }
            for i in identities
        ],
        "shipment_from_snapshot": shipment_from_snapshot,
        "shipment_from_provider": shipment_from_provider,
    }


@router.get("/after-sales/resolve")
def resolve_after_sale(
    platform: str = Query(...),
    external_order_id: str = Query(...),
    account_id: str = Query(""),
    source_system: str = Query("platform"),
    db: Session = Depends(get_db),
) -> dict:
    """
    Resolve after-sale data through the unified order identity layer.

    Chain:
      external_order_id -> resolve_order_id -> order_core.id
      -> order_identity_mapping -> after_sale_case lookup
      -> existing provider for live after-sale data

    This proves after-sale queries can go through the internal order key
    instead of directly using external order IDs.
    """
    from app.services.identity_service import resolve_order_id as _resolve_order_id
    from app.repositories.order_identity_repository import get_by_order_id as _get_identities
    from app.repositories.order_core_repository import get_by_id as _get_order
    from domain_models.models.after_sale_case import AfterSaleCase

    internal_order_id = _resolve_order_id(db, source_system, platform, external_order_id, account_id)
    if internal_order_id is None:
        internal_order_id = _resolve_order_id(db, platform, platform, external_order_id, account_id)
    if internal_order_id is None:
        internal_order_id = _resolve_order_id(db, "odoo", platform, external_order_id, account_id)
    if internal_order_id is None:
        internal_order_id = _resolve_order_id(db, "odoo", "odoo", external_order_id, "demo")
    if internal_order_id is None:
        return {
            "internal_order_id": None,
            "resolved": False,
            "after_sale_from_db": None,
            "after_sale_from_provider": None,
        }

    order = _get_order(db, internal_order_id)
    identities = _get_identities(db, internal_order_id)

    after_sale_from_db = None
    for identity in identities:
        cases = db.query(AfterSaleCase).filter_by(
            platform=identity.platform,
            order_id=identity.external_order_id,
        ).all()
        if cases:
            c = cases[0]
            after_sale_from_db = {
                "id": c.id,
                "platform": c.platform,
                "after_sale_id": c.after_sale_id,
                "order_id": c.order_id,
                "case_type": c.case_type,
                "status": c.status,
                "reason": c.reason,
            }
            break

    after_sale_from_provider = None
    try:
        provider = _get_provider(platform)
        dto = provider.get_after_sale(external_order_id)
        after_sale_from_provider = {
            "platform": dto.platform,
            "after_sale_id": dto.after_sale_id,
            "order_id": dto.order_id,
            "type": dto.type,
            "type_name": dto.type_name,
            "status": dto.status,
            "status_name": dto.status_name,
            "apply_amount": dto.apply_amount,
            "approve_amount": dto.approve_amount,
            "reason": dto.reason,
        }
    except Exception as e:
        after_sale_from_provider = {"error": str(e)}

    return {
        "internal_order_id": internal_order_id,
        "resolved": True,
        "customer_id": order.customer_id if order else None,
        "current_status": order.current_status if order else None,
        "identities": [
            {
                "source_system": i.source_system,
                "platform": i.platform,
                "account_id": i.account_id,
                "external_order_id": i.external_order_id,
                "external_status": i.external_status,
                "is_primary": i.is_primary,
            }
            for i in identities
        ],
        "after_sale_from_db": after_sale_from_db,
        "after_sale_from_provider": after_sale_from_provider,
    }