import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/mock/wecom-kf", tags=["mock-wecom-kf"])


def _load_fixture(filename: str) -> dict:
    fixture_path = Path(__file__).parent.parent / "data" / "wecom_kf" / filename
    if not fixture_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture not found: {filename}")
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


class WecomTokenRequest(BaseModel):
    corpid: str | None = None
    corpsecret: str | None = None


class WecomTokenResponse(BaseModel):
    access_token: str
    expires_in: int
    refresh_token: str
    corp_id: str
    agent_id: str


@router.post("/token", response_model=WecomTokenResponse)
def token(request: WecomTokenRequest | None = None) -> WecomTokenResponse:
    data = _load_fixture("token_response.json")
    return WecomTokenResponse(**data)


class WecomMessageSyncRequest(BaseModel):
    msgid: str | None = None
    from_user: str | None = None
    to_user: str | None = None
    msg_type: str | None = None
    content: str | None = None
    session_id: str | None = None


class WecomMessageSyncResponse(BaseModel):
    msgid: str
    from_user: str
    to_user: str
    create_time: int
    msg_type: str
    content: str
    session_id: str


@router.post("/messages/sync", response_model=WecomMessageSyncResponse)
def message_sync(request: WecomMessageSyncRequest | None = None) -> WecomMessageSyncResponse:
    data = _load_fixture("message_sample.json")
    if request:
        if request.msgid:
            data["msgid"] = request.msgid
        if request.from_user:
            data["from_user"] = request.from_user
        if request.to_user:
            data["to_user"] = request.to_user
        if request.msg_type:
            data["msg_type"] = request.msg_type
        if request.content:
            data["content"] = request.content
        if request.session_id:
            data["session_id"] = request.session_id
    return WecomMessageSyncResponse(**data)


class WecomServiceStateRequest(BaseModel):
    user_id: str | None = None
    service_state: str | None = None


class WecomServiceStateResponse(BaseModel):
    msgid: str
    user_id: str
    service_state: str
    service_state_name: str
    from_user: str
    to_user: str


@router.post("/service-state/trans", response_model=WecomServiceStateResponse)
def service_state_transfer(request: WecomServiceStateRequest | None = None) -> WecomServiceStateResponse:
    data = _load_fixture("service_state_sample.json")
    if request:
        if request.user_id:
            data["user_id"] = request.user_id
        if request.service_state:
            data["service_state"] = request.service_state
            state_map = {
                "SERVING": "服务中",
                "WAITING": "排队中",
                "ENDED": "已结束"
            }
            data["service_state_name"] = state_map.get(request.service_state, "未知")
    return WecomServiceStateResponse(**data)


class WecomEventMessageRequest(BaseModel):
    event_type: str | None = None
    agent_id: str | None = None
    user_id: str | None = None
    msg_type: str | None = None
    content: str | None = None


class WecomEventMessageResponse(BaseModel):
    msgid: str
    event_type: str
    agent_id: str
    user_id: str
    msg_type: str


@router.post("/event-message/send", response_model=WecomEventMessageResponse)
def event_message_send(request: WecomEventMessageRequest | None = None) -> WecomEventMessageResponse:
    data = _load_fixture("event_message_sample.json")
    if request:
        if request.event_type:
            data["event_type"] = request.event_type
        if request.agent_id:
            data["agent_id"] = request.agent_id
        if request.user_id:
            data["user_id"] = request.user_id
        if request.msg_type:
            data["msg_type"] = request.msg_type
    return WecomEventMessageResponse(**data)