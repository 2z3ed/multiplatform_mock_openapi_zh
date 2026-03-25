import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/mock/douyin-shop", tags=["mock-douyin-shop"])


def _load_fixture(filename: str) -> dict:
    fixture_path = Path(__file__).parent.parent / "data" / "douyin_shop" / filename
    if not fixture_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Fixture not found: {filename}")
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


class DouyinTokenRequest(BaseModel):
    app_key: str | None = None
    app_secret: str | None = None
    code: str | None = None


class DouyinTokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    scope: str


@router.post("/auth/token", response_model=DouyinTokenResponse)
def auth_token(request: DouyinTokenRequest | None = None) -> DouyinTokenResponse:
    data = _load_fixture("token_response.json")
    return DouyinTokenResponse(**data)


@router.get("/orders/{order_id}")
def get_order(order_id: str) -> dict:
    data = _load_fixture("order_sample.json")
    data["orderId"] = order_id
    return data


@router.get("/refunds/{after_sale_id}")
def get_refund(after_sale_id: str) -> dict:
    data = _load_fixture("refund_sample.json")
    data["refundId"] = after_sale_id
    return data


@router.get("/products/{product_id}")
def get_product(product_id: str) -> dict:
    data = _load_fixture("product_sample.json")
    data["productId"] = product_id
    return data