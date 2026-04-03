"""
Identity service: minimal helpers for cross-system identity lookup.

This service does NOT contain business logic.
It only provides lookup helpers across customer_identity_mapping and order_identity_mapping.
"""
from sqlalchemy.orm import Session

from domain_models.models.customer import Customer
from app.repositories.customer_identity_repository import (
    get_by_external_id as _get_customer_by_external,
    get_by_customer_id as _get_customer_identities,
    create_primary as _create_customer_identity,
)
from app.repositories.order_identity_repository import (
    get_by_external_id as _get_order_by_external,
    get_by_order_id as _get_order_identities,
    create_primary as _create_order_identity,
)
from app.repositories.order_core_repository import (
    get_by_id as _get_order_core,
    create as _create_order_core,
)
from app.repositories.conversation_order_repository import (
    get_by_conversation as _get_links_by_conversation,
    get_by_order as _get_links_by_order,
    create as _create_link,
)


def resolve_customer_id(
    db: Session,
    source_system: str,
    platform: str,
    external_user_id: str,
    account_id: str = "",
) -> int | None:
    """
    Resolve internal customer_id from external identity.
    Returns None if no mapping exists.
    """
    mapping = _get_customer_by_external(db, source_system, platform, account_id, external_user_id)
    return mapping.customer_id if mapping else None


def resolve_order_id(
    db: Session,
    source_system: str,
    platform: str,
    external_order_id: str,
    account_id: str = "",
) -> int | None:
    """
    Resolve internal order_core.id from external order identity.
    Returns None if no mapping exists.
    """
    mapping = _get_order_by_external(db, source_system, platform, account_id, external_order_id)
    return mapping.order_id if mapping else None


def get_or_create_customer_identity(
    db: Session,
    source_system: str,
    platform: str,
    external_user_id: str,
    external_user_name: str | None = None,
    account_id: str = "",
) -> int:
    """
    Resolve internal customer_id from external identity.
    If no mapping exists, try to find existing customer by (platform, platform_customer_id).
    If no customer exists, create a new one and the identity mapping.
    Returns the internal customer_id.
    """
    mapping = _get_customer_by_external(db, source_system, platform, account_id, external_user_id)
    if mapping:
        return mapping.customer_id

    existing_customer = db.query(Customer).filter_by(
        platform=platform,
        platform_customer_id=external_user_id,
    ).first()
    if existing_customer:
        _create_customer_identity(
            db,
            customer_id=existing_customer.id,
            source_system=source_system,
            platform=platform,
            external_user_id=external_user_id,
            external_user_name=external_user_name,
            account_id=account_id,
        )
        return existing_customer.id

    customer = Customer(
        platform=platform,
        platform_customer_id=external_user_id,
        display_name=external_user_name,
    )
    db.add(customer)
    db.flush()
    _create_customer_identity(
        db,
        customer_id=customer.id,
        source_system=source_system,
        platform=platform,
        external_user_id=external_user_id,
        external_user_name=external_user_name,
        account_id=account_id,
    )
    return customer.id


def bind_order_to_conversation(
    db: Session,
    conversation_id: int,
    order_id: int,
    link_type: str = "bound",
) -> dict:
    """
    Bind an order to a conversation.
    Returns existing link if already bound, or creates a new one.
    """
    existing = _get_links_by_conversation(db, conversation_id)
    for link in existing:
        if link.order_id == order_id:
            return {"link_id": link.id, "link_type": link.link_type, "already_existed": True}

    link = _create_link(db, conversation_id, order_id, link_type)
    return {"link_id": link.id, "link_type": link.link_type, "already_existed": False}


def list_order_ids_for_conversation(db: Session, conversation_id: int) -> list[dict]:
    """
    List all order_core IDs linked to a conversation.
    Returns list of {order_id, link_type}.
    """
    links = _get_links_by_conversation(db, conversation_id)
    return [{"order_id": link.order_id, "link_type": link.link_type} for link in links]


def list_conversation_ids_for_order(db: Session, order_id: int) -> list[dict]:
    """
    List all conversation IDs linked to an order.
    Returns list of {conversation_id, link_type}.
    """
    links = _get_links_by_order(db, order_id)
    return [{"conversation_id": link.conversation_id, "link_type": link.link_type} for link in links]

