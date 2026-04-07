from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import httpx

from shared_db import get_db
from domain_models.models.message import Message
from domain_models.models.conversation import Conversation

router = APIRouter(prefix="/api/messages", tags=["messages"])

PLATFORM_SIM_URL = os.getenv("PLATFORM_SIM_URL", "http://localhost:9000")


class MessageSendRequest(BaseModel):
    conversation_id: str
    content: str
    sender_type: str = "agent"
    sender_id: Optional[str] = None


class InboundMessageRequest(BaseModel):
    conversation_id: str
    content: str
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


def _resolve_conv(db: Session, conversation_id: str):
    """Resolve conversation_id string to (conv_pk, platform)."""
    try:
        conv_pk = int(conversation_id)
    except (ValueError, TypeError):
        return None, None
    conv = db.query(Conversation).filter(Conversation.id == conv_pk).first()
    if conv is None:
        return None, None
    return conv_pk, conv.platform


@router.post("", response_model=MessageResponse)
async def send_message(request: MessageSendRequest, db: Session = Depends(get_db)):
    conv_pk, platform = _resolve_conv(db, request.conversation_id)
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
        try:
            user_reply = await _get_user_reply_with_retry(request.conversation_id, platform or "jd", request.content, db)
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
        conversation_id=request.conversation_id,
        sender_type=request.sender_type,
        content=request.content,
        sent_at=sent_at,
        user_reply=user_reply,
        error=error_msg,
    )


@router.get("/{conversation_id}")
async def get_messages(conversation_id: str, db: Session = Depends(get_db)):
    conv_pk, _ = _resolve_conv(db, conversation_id)
    if conv_pk is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

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


@router.post("/inbound", response_model=MessageResponse)
def send_inbound_message(request: InboundMessageRequest, db: Session = Depends(get_db)):
    """Minimal inbound (customer) message endpoint. Does not depend on PlatformSim."""
    conv_pk, _ = _resolve_conv(db, request.conversation_id)
    if conv_pk is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    sent_at = datetime.utcnow()
    msg = Message(
        conversation_id=conv_pk,
        sender_type="customer",
        sender_id=request.sender_id,
        content=request.content,
        sent_at=sent_at,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return MessageResponse(
        id=msg.id,
        conversation_id=request.conversation_id,
        sender_type="customer",
        content=request.content,
        sent_at=sent_at,
    )


async def _get_user_reply_with_retry(
    conversation_id: str,
    platform: str,
    agent_message: str,
    db: Session
) -> Optional[str]:
    conv_pk, _ = _resolve_conv(db, conversation_id)
    run_id = None

    if conv_pk:
        try:
            result = db.execute(text("SELECT extra_json FROM conversation WHERE id = :id"), {"id": conv_pk})
            row = result.fetchone()
            if row and row[0]:
                extra = row[0]
                if isinstance(extra, str):
                    import json
                    extra = json.loads(extra)
                run_id = extra.get('platform_sim_run_id') if extra else None
        except Exception:
            pass

    if run_id:
        try:
            user_reply = await _call_agent_message(run_id, conversation_id, agent_message)
            return user_reply
        except RunNotFoundError:
            run_id = None

    try:
        run_id = await _create_run(conversation_id, platform)
    except Exception:
        return None

    if conv_pk:
        try:
            import json
            result = db.execute(text("SELECT extra_json FROM conversation WHERE id = :id"), {"id": conv_pk})
            row = result.fetchone()
            existing_extra = row[0] if row and row[0] else {}
            if isinstance(existing_extra, str):
                existing_extra = json.loads(existing_extra)
            existing_extra['platform_sim_run_id'] = run_id
            stmt = text("UPDATE conversation SET extra_json = :extra_json WHERE id = :id")
            db.execute(stmt, {"extra_json": json.dumps(existing_extra), "id": conv_pk})
            db.commit()
        except Exception:
            pass

    try:
        user_reply = await _call_agent_message(run_id, conversation_id, agent_message)
        return user_reply
    except RunNotFoundError:
        return None
    except Exception:
        return None


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
