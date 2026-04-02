from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import httpx

from shared_db import get_db
from domain_models.models.message import Message
from domain_models.models.conversation import Conversation

router = APIRouter(prefix="/api/messages", tags=["messages"])

CONVERSATION_PK_MAP = {
    "conv1": 1, "conv2": 2, "conv3": 3, "conv4": 4, "conv5": 5, "conv6": 6, "conv7": 7,
}

PLATFORM_SIM_URL = os.getenv("PLATFORM_SIM_URL", "http://localhost:9000")


class MessageSendRequest(BaseModel):
    conversation_id: str
    content: str
    sender_type: str = "agent"
    sender_id: Optional[str] = None


class MessageResponse(BaseModel):
    id: int
    conversation_id: str
    sender_type: str
    content: str
    sent_at: datetime
    user_reply: Optional[str] = None
    error: Optional[str] = None


class RunNotFoundError(Exception):
    pass


@router.post("", response_model=MessageResponse)
async def send_message(request: MessageSendRequest, db: Session = Depends(get_db)):
    conversation_id = request.conversation_id
    conv_pk = CONVERSATION_PK_MAP.get(conversation_id)
    if conv_pk is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    sent_at = datetime.utcnow()

    agent_msg = Message(
        conversation_id=conv_pk,
        sender_type=request.sender_type,
        sender_id=request.sender_id,
        content=request.content,
        sent_at=sent_at,
    )
    db.add(agent_msg)
    db.commit()
    db.refresh(agent_msg)

    user_reply = None
    error_msg = None
    
    if request.sender_type == "agent":
        platform = _get_platform_by_conversation(conversation_id)
        
        try:
            user_reply = await _get_user_reply_with_retry(conversation_id, platform, request.content, db)
            if user_reply:
                user_msg = Message(
                    conversation_id=conv_pk,
                    sender_type="customer",
                    sender_id=None,
                    content=user_reply,
                    sent_at=datetime.utcnow(),
                )
                db.add(user_msg)
                db.commit()
        except RunNotFoundError as e:
            error_msg = f"Run not found and failed to recreate: {str(e)}"
        except httpx.ConnectError:
            error_msg = "PlatformSim service unavailable: connection refused"
        except httpx.TimeoutException:
            error_msg = "PlatformSim service unavailable: timeout"
        except httpx.HTTPStatusError as e:
            error_msg = f"PlatformSim HTTP error: {e.response.status_code}"
        except Exception as e:
            error_msg = f"PlatformSim error: {str(e)}"

    return MessageResponse(
        id=agent_msg.id,
        conversation_id=conversation_id,
        sender_type=request.sender_type,
        content=request.content,
        sent_at=sent_at,
        user_reply=user_reply,
        error=error_msg,
    )


@router.get("/{conversation_id}")
async def get_messages(conversation_id: str, db: Session = Depends(get_db)):
    if conversation_id not in CONVERSATION_PK_MAP:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conv_pk = CONVERSATION_PK_MAP[conversation_id]
    
    messages = db.query(Message).filter(
        Message.conversation_id == conv_pk
    ).order_by(Message.sent_at.asc()).all()
    
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": msg.id,
                "conversation_id": conversation_id,
                "sender_type": msg.sender_type,
                "sender_id": msg.sender_id,
                "content": msg.content,
                "sent_at": msg.sent_at.isoformat() if msg.sent_at else None,
            }
            for msg in messages
        ]
    }


async def _get_user_reply_with_retry(
    conversation_id: str, 
    platform: str, 
    agent_message: str, 
    db: Session
) -> Optional[str]:
    conv_pk = CONVERSATION_PK_MAP.get(conversation_id)
    run_id = None
    
    if conv_pk:
        conv = db.query(Conversation).filter(Conversation.id == conv_pk).first()
        if conv and conv.extra_json:
            run_id = conv.extra_json.get('platform_sim_run_id')
    
    if run_id:
        try:
            user_reply = await _call_agent_message(run_id, conversation_id, agent_message)
            return user_reply
        except RunNotFoundError:
            pass
    
    run_id = await _create_run(conversation_id, platform)
    
    if conv_pk:
        conv = db.query(Conversation).filter(Conversation.id == conv_pk).first()
        if conv:
            if conv.extra_json is None:
                conv.extra_json = {}
            conv.extra_json['platform_sim_run_id'] = run_id
            db.commit()
    
    user_reply = await _call_agent_message(run_id, conversation_id, agent_message)
    return user_reply


async def _create_run(conversation_id: str, platform: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{PLATFORM_SIM_URL}/conversation-studio/runs",
            json={
                "platform": platform,
                "conversation_id": conversation_id,
                "scenario_name": "default",
                "max_turns": 100,
            }
        )
        if resp.status_code in (200, 201):
            data = resp.json()
            run_id = data.get("run_id")
            if run_id:
                return run_id
            raise Exception("Create run response missing run_id")
        raise Exception(f"Failed to create run: status {resp.status_code}")


async def _call_agent_message(run_id: str, conversation_id: str, agent_message: str) -> str:
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{PLATFORM_SIM_URL}/conversation-studio/runs/{run_id}/agent-message",
            json={
                "agent_message": agent_message,
                "conversation_id": conversation_id,
            }
        )
        
        if resp.status_code == 200:
            data = resp.json()
            return data.get("user_message")
        
        if resp.status_code == 404:
            raise RunNotFoundError(f"Run {run_id} not found")
        
        resp.raise_for_status()
        raise Exception(f"Unexpected status code: {resp.status_code}")


def _get_platform_by_conversation(conversation_id: str) -> str:
    platform_map = {
        "conv1": "jd", "conv2": "jd",
        "conv3": "taobao", "conv4": "taobao",
        "conv5": "douyin_shop", "conv6": "douyin_shop",
        "conv7": "wecom_kf",
    }
    return platform_map.get(conversation_id, "jd")
