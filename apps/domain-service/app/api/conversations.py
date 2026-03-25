from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

MOCK_CONVERSATIONS = [
    {
        "id": "conv_001",
        "platform": "jd",
        "customer_id": "customer_001",
        "customer_nick": "用户_13800138000",
        "status": "active",
        "assigned_agent": None,
        "unread_count": 2,
        "last_message_time": "2024-03-20T15:00:00Z",
        "created_at": "2024-03-15T10:00:00Z"
    },
    {
        "id": "conv_002",
        "platform": "douyin_shop",
        "customer_id": "customer_002",
        "customer_nick": "抖音用户_13900139000",
        "status": "active",
        "assigned_agent": "agent_001",
        "unread_count": 0,
        "last_message_time": "2024-03-20T14:30:00Z",
        "created_at": "2024-03-16T11:00:00Z"
    },
    {
        "id": "conv_003",
        "platform": "wecom_kf",
        "customer_id": "customer_003",
        "customer_nick": "微信用户_abc",
        "status": "waiting",
        "assigned_agent": None,
        "unread_count": 1,
        "last_message_time": "2024-03-20T16:00:00Z",
        "created_at": "2024-03-18T09:00:00Z"
    }
]


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
def get_messages(conversation_id: str, skip: int = 0, limit: int = 50) -> dict:
    mock_messages = [
        {
            "id": "msg_001",
            "conversation_id": conversation_id,
            "direction": "inbound",
            "content": "你好，我想查询订单状态",
            "sender": "customer",
            "create_time": "2024-03-20T14:00:00Z"
        },
        {
            "id": "msg_002",
            "conversation_id": conversation_id,
            "direction": "outbound",
            "content": "您好，请问您的订单号是多少？",
            "sender": "agent",
            "create_time": "2024-03-20T14:05:00Z"
        }
    ]
    return {
        "total": len(mock_messages),
        "items": mock_messages[skip:skip + limit]
    }


@router.post("/{conversation_id}/assign")
def assign_conversation(conversation_id: str, agent_id: str) -> dict:
    for conv in MOCK_CONVERSATIONS:
        if conv["id"] == conversation_id:
            conv["assigned_agent"] = agent_id
            return {"status": "ok", "conversation_id": conversation_id, "assigned_agent": agent_id}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")


@router.post("/{conversation_id}/handoff")
def handoff_conversation(conversation_id: str, target_agent: str) -> dict:
    for conv in MOCK_CONVERSATIONS:
        if conv["id"] == conversation_id:
            conv["assigned_agent"] = target_agent
            return {"status": "ok", "conversation_id": conversation_id, "handoff_to": target_agent}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")