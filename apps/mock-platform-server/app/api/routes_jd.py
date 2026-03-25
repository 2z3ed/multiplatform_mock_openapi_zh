import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/mock/jd", tags=["mock-jd"])


def _load_fixture(filename: str) -> dict:
    fixture_path = Path(__file__).parent.parent / "data" / "jd" / filename
    if not fixture_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture not found: {filename}")
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


class JdTokenRequest(BaseModel):
    app_key: str | None = None
    app_secret: str | None = None


class JdTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str


@router.post("/oauth/token", response_model=JdTokenResponse)
def oauth_token(request: JdTokenRequest | None = None) -> JdTokenResponse:
    data = _load_fixture("token_response.json")
    return JdTokenResponse(**data)


@router.get("/orders/{order_id}")
def get_order(order_id: str) -> dict:
    data = _load_fixture("order_sample.json")
    data["orderId"] = order_id
    return data


@router.get("/shipments/{order_id}")
def get_shipment(order_id: str) -> dict:
    data = _load_fixture("shipment_sample.json")
    data["orderId"] = order_id
    return data


@router.get("/after-sales/{after_sale_id}")
def get_after_sale(after_sale_id: str) -> dict:
    data = _load_fixture("after_sale_sample.json")
    data["afterSaleId"] = after_sale_id
    return data