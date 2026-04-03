from sqlalchemy.orm import Session
from domain_models.models.order_identity_mapping import OrderIdentityMapping


def get_by_external_id(
    db: Session,
    source_system: str,
    platform: str,
    account_id: str,
    external_order_id: str,
) -> OrderIdentityMapping | None:
    return db.query(OrderIdentityMapping).filter_by(
        source_system=source_system,
        platform=platform,
        account_id=account_id,
        external_order_id=external_order_id,
    ).first()


def get_by_order_id(db: Session, order_id: int) -> list[OrderIdentityMapping]:
    return db.query(OrderIdentityMapping).filter_by(order_id=order_id).all()


def create_primary(
    db: Session,
    order_id: int,
    source_system: str,
    platform: str,
    external_order_id: str,
    external_status: str | None = None,
    account_id: str = "",
) -> OrderIdentityMapping:
    mapping = OrderIdentityMapping(
        order_id=order_id,
        source_system=source_system,
        platform=platform,
        account_id=account_id,
        external_order_id=external_order_id,
        external_status=external_status,
        is_primary=True,
    )
    db.add(mapping)
    db.flush()
    return mapping
