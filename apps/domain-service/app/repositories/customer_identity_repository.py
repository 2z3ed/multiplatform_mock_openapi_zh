from sqlalchemy.orm import Session
from domain_models.models.customer_identity_mapping import CustomerIdentityMapping


def get_by_external_id(
    db: Session,
    source_system: str,
    platform: str,
    account_id: str,
    external_user_id: str,
) -> CustomerIdentityMapping | None:
    return db.query(CustomerIdentityMapping).filter_by(
        source_system=source_system,
        platform=platform,
        account_id=account_id,
        external_user_id=external_user_id,
    ).first()


def get_by_customer_id(db: Session, customer_id: int) -> list[CustomerIdentityMapping]:
    return db.query(CustomerIdentityMapping).filter_by(customer_id=customer_id).all()


def create_primary(
    db: Session,
    customer_id: int,
    source_system: str,
    platform: str,
    external_user_id: str,
    external_user_name: str | None = None,
    account_id: str = "",
) -> CustomerIdentityMapping:
    mapping = CustomerIdentityMapping(
        customer_id=customer_id,
        source_system=source_system,
        platform=platform,
        account_id=account_id,
        external_user_id=external_user_id,
        external_user_name=external_user_name,
        is_primary=True,
    )
    db.add(mapping)
    db.flush()
    return mapping
