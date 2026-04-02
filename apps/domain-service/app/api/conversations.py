from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.services.audit_service import get_audit_service, AuditService
from shared_db import get_db
from domain_models.models.message import Message

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

MOCK_CONVERSATIONS = [
    {
        "id": "conv1",
        "conversation_pk": 1,
        "platform": "jd",
        "customer_id": "jd_user_001",
        "customer_pk": 1,
        "customer_nick": "李明",
        "status": "active",
        "assigned_agent": None,
        "unread_count": 2,
        "last_message_time": "2026-03-30T09:00:00Z",
        "created_at": "2026-03-28T20:15:00Z"
    },
    {
        "id": "conv2",
        "conversation_pk": 2,
        "platform": "jd",
        "customer_id": "jd_user_002",
        "customer_pk": 2,
        "customer_nick": "王芳",
        "status": "active",
        "assigned_agent": "agent_001",
        "unread_count": 1,
        "last_message_time": "2026-03-30T10:30:00Z",
        "created_at": "2026-03-29T16:20:00Z"
    },
    {
        "id": "conv3",
        "conversation_pk": 3,
        "platform": "taobao",
        "customer_id": "tb_user_001",
        "customer_pk": 3,
        "customer_nick": "张婷",
        "status": "active",
        "assigned_agent": "agent_001",
        "unread_count": 3,
        "last_message_time": "2026-03-30T08:00:00Z",
        "created_at": "2026-03-28T11:30:00Z"
    },
    {
        "id": "conv4",
        "conversation_pk": 4,
        "platform": "taobao",
        "customer_id": "tb_user_002",
        "customer_pk": 4,
        "customer_nick": "陈浩",
        "status": "waiting",
        "assigned_agent": None,
        "unread_count": 1,
        "last_message_time": "2026-03-30T11:00:00Z",
        "created_at": "2026-03-30T10:00:00Z"
    },
    {
        "id": "conv5",
        "conversation_pk": 5,
        "platform": "douyin_shop",
        "customer_id": "douyin_user_001",
        "customer_pk": 5,
        "customer_nick": "刘洋",
        "status": "active",
        "assigned_agent": None,
        "unread_count": 2,
        "last_message_time": "2026-03-30T09:30:00Z",
        "created_at": "2026-03-30T09:15:00Z"
    },
    {
        "id": "conv6",
        "conversation_pk": 6,
        "platform": "douyin_shop",
        "customer_id": "douyin_user_002",
        "customer_pk": 6,
        "customer_nick": "赵雪",
        "status": "active",
        "assigned_agent": "agent_002",
        "unread_count": 1,
        "last_message_time": "2026-03-30T07:00:00Z",
        "created_at": "2026-03-28T15:20:00Z"
    },
    {
        "id": "conv7",
        "conversation_pk": 7,
        "platform": "wecom_kf",
        "customer_id": "wecom_user_001",
        "customer_pk": 7,
        "customer_nick": "微信用户_孙伟",
        "status": "waiting",
        "assigned_agent": None,
        "unread_count": 1,
        "last_message_time": "2026-03-30T10:00:00Z",
        "created_at": "2026-03-30T09:45:00Z"
    }
]

CONVERSATION_PK_MAP = {
    "conv1": 1, "conv2": 2, "conv3": 3, "conv4": 4, "conv5": 5, "conv6": 6, "conv7": 7,
}


@router.get("")
def list_conversations(
    platform: str | None = None,
    status: str | None = None,
    assigned_agent: str | None = None,
    skip: int = 0,
    limit: int = 20
) -> dict:
    result = MOCK_CONVERSATIONS
    if platform:
        result = [c for c in result if c["platform"] == platform]
    if status:
        result = [c for c in result if c["status"] == status]
    if assigned_agent is not None:
        if assigned_agent == "":
            result = [c for c in result if c["assigned_agent"] is None]
        else:
            result = [c for c in result if c["assigned_agent"] == assigned_agent]
    return {
        "total": len(result),
        "items": result[skip:skip + limit]
    }


@router.get("/{conversation_id}")
def get_conversation(conversation_id: str) -> dict:
    for conv in MOCK_CONVERSATIONS:
        if conv["id"] == conversation_id:
            return conv
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")


@router.get("/{conversation_id}/messages")
def get_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> dict:
    conv = None
    for c in MOCK_CONVERSATIONS:
        if c["id"] == conversation_id:
            conv = c
            break

    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    conv_pk = CONVERSATION_PK_MAP.get(conversation_id)
    messages = []
    
    if conv_pk:
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
    for conv in MOCK_CONVERSATIONS:
        if conv["id"] == conversation_id:
            old_agent = conv["assigned_agent"]
            conv["assigned_agent"] = agent_id
            audit_svc.conversation_assigned(
                conversation_id=conversation_id,
                agent_id=agent_id,
                assigned_by="api"
            )
            return {"status": "ok", "conversation_id": conversation_id, "assigned_agent": agent_id}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")


@router.post("/{conversation_id}/handoff")
def handoff_conversation(
    conversation_id: str,
    target_agent: str,
    db: Session = Depends(get_db),
    audit_svc: AuditService = Depends(lambda db=Depends(get_db): get_audit_service(db))
) -> dict:
    for conv in MOCK_CONVERSATIONS:
        if conv["id"] == conversation_id:
            old_agent = conv["assigned_agent"]
            conv["assigned_agent"] = target_agent
            audit_svc.conversation_handed_off(
                conversation_id=conversation_id,
                from_agent=old_agent or "none",
                to_agent=target_agent
            )
            return {"status": "ok", "conversation_id": conversation_id, "handoff_to": target_agent}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
