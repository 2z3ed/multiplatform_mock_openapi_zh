from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.services.audit_service import get_audit_service, AuditService
from app.repositories.conversation_repository import list_all as _list_conversations, get_by_id as _get_conversation
from shared_db import get_db
from domain_models.models.message import Message

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


def _conv_to_dict(conv) -> dict:
    """Convert DB Conversation to API dict."""
    customer_id = None
    customer_nick = None
    if hasattr(conv, 'customer') and conv.customer:
        customer_id = conv.customer.platform_customer_id
        customer_nick = conv.customer.display_name

    return {
        "id": str(conv.id),
        "conversation_pk": conv.id,
        "platform": conv.platform,
        "customer_id": customer_id,
        "customer_pk": conv.customer_id,
        "customer_nick": customer_nick,
        "status": conv.status,
        "assigned_agent": conv.assigned_agent_id,
        "subject": conv.subject,
        "unread_count": 0,
        "last_message_time": conv.updated_at.isoformat() if conv.updated_at else None,
        "created_at": conv.created_at.isoformat() if conv.created_at else None,
        "extra_json": conv.extra_json,
    }


@router.get("")
def list_conversations(
    platform: str | None = None,
    status: str | None = None,
    assigned_agent: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
) -> dict:
    conversations = _list_conversations(db, platform=platform, status=status, skip=skip, limit=limit)
    total = _list_conversations.__code__.co_consts  # placeholder, use count
    from app.repositories.conversation_repository import count_all
    total = count_all(db, platform=platform, status=status)

    items = [_conv_to_dict(c) for c in conversations]

    if assigned_agent is not None:
        if assigned_agent == "":
            items = [i for i in items if not i.get("assigned_agent")]
        else:
            items = [i for i in items if i.get("assigned_agent") == assigned_agent]

    return {
        "total": total,
        "items": items
    }


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str, db: Session = Depends(get_db)) -> dict:
    try:
        conv_id = int(conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    conv = _get_conversation(db, conv_id)
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return _conv_to_dict(conv)


@router.get("/{conversation_id}/messages")
def get_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> dict:
    try:
        conv_pk = int(conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    conv = _get_conversation(db, conv_pk)
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    messages = []
    db_messages = db.query(Message).filter(
        Message.conversation_id == conv_pk
    ).order_by(Message.sent_at.asc()).all()

    for msg in db_messages:
        messages.append({
            "id": f"db_{msg.id}",
            "conversation_id": conversation_id,
            "direction": "outbound" if msg.sender_type == "agent" else "inbound",
            "content": msg.content,
            "sender": msg.sender_type,
            "create_time": msg.sent_at.isoformat() if msg.sent_at else None,
        })

    return {
        "total": len(messages),
        "items": messages[skip:skip + limit]
    }


@router.post("/{conversation_id}/assign")
def assign_conversation(
    conversation_id: str,
    agent_id: str,
    db: Session = Depends(get_db),
    audit_svc: AuditService = Depends(lambda db=Depends(get_db): get_audit_service(db))
) -> dict:
    try:
        conv_pk = int(conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    conv = _get_conversation(db, conv_pk)
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    old_agent = conv.assigned_agent_id
    conv.assigned_agent_id = agent_id
    db.commit()

    audit_svc.conversation_assigned(
        conversation_id=conversation_id,
        agent_id=agent_id,
        assigned_by="api"
    )
    return {"status": "ok", "conversation_id": conversation_id, "assigned_agent": agent_id}


@router.post("/{conversation_id}/handoff")
def handoff_conversation(
    conversation_id: str,
    target_agent: str,
    db: Session = Depends(get_db),
    audit_svc: AuditService = Depends(lambda db=Depends(get_db): get_audit_service(db))
) -> dict:
    try:
        conv_pk = int(conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    conv = _get_conversation(db, conv_pk)
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    old_agent = conv.assigned_agent_id
    conv.assigned_agent_id = target_agent
    db.commit()

    audit_svc.conversation_handed_off(
        conversation_id=conversation_id,
        from_agent=old_agent or "none",
        to_agent=target_agent
    )
    return {"status": "ok", "conversation_id": conversation_id, "handoff_to": target_agent}


@router.post("/{conversation_id}/orders/{order_id}/bind")
def bind_order_to_conversation(
    conversation_id: str,
    order_id: int,
    link_type: str = "bound",
    db: Session = Depends(get_db),
) -> dict:
    from app.services.identity_service import bind_order_to_conversation as _bind

    try:
        conv_pk = int(conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    result = _bind(db, conv_pk, order_id, link_type)
    return {
        "status": "ok",
        "conversation_id": conversation_id,
        "order_id": order_id,
        "link_type": result["link_type"],
        "already_existed": result["already_existed"],
    }


@router.get("/{conversation_id}/orders")
def list_conversation_orders(
    conversation_id: str,
    db: Session = Depends(get_db),
) -> dict:
    from app.services.identity_service import list_order_ids_for_conversation as _list_orders

    try:
        conv_pk = int(conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    orders = _list_orders(db, conv_pk)
    return {
        "conversation_id": conversation_id,
        "orders": orders,
    }


@router.get("/{conversation_id}/context")
def get_conversation_context(
    conversation_id: str,
    db: Session = Depends(get_db),
) -> dict:
    from app.services.context_aggregation_service import aggregate_conversation_context

    try:
        conv_pk = int(conversation_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return aggregate_conversation_context(db, conv_pk)
