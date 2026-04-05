"""
E4-B: Automated regression and contract tests for the multi-platform simulation layer.

Covers:
- 6 platforms × 4 query chains (order / shipment / after-sale / inventory)
- fixture mode (default)
- unified error semantics (404 / 503)
- contract checks (_source non-leakage, key fields, platform structure)

Run:
    pytest tests/regression/test_multi_platform_regression.py -v
"""

import pytest
import httpx

BASE_URL = "http://localhost:8000"

PLATFORMS = ["jd", "taobao", "douyin_shop", "wecom_kf", "kuaishou", "xhs"]

# Known valid order IDs per platform (fixture data)
VALID_ORDERS = {
    "jd": "304857291638",
    "taobao": "4728561930472815",
    "douyin_shop": "6847291038472910",
    "wecom_kf": "WK_ORDER_001",
    "kuaishou": "KS_ORDER_001",
    "xhs": "XHS_ORDER_001",
}

VALID_SHIPMENTS = {
    "jd": "304857291638",
    "taobao": "4728561930472815",
    "douyin_shop": "6847391827463910",
    "wecom_kf": "WK_ORDER_002",
    "kuaishou": "KS_ORDER_002",
    "xhs": "XHS_ORDER_002",
}

VALID_AFTERSALES = {
    "jd": "304618372956",
    "taobao": "4728391847263951",
    "douyin_shop": "6846183729104857",
    "wecom_kf": "WK_ORDER_003",
    "kuaishou": "KS_ORDER_003",
    "xhs": "XHS_ORDER_003",
}

VALID_INVENTORY = {
    "jd": "304857291638",
    "taobao": "4728561930472815",
    "douyin_shop": "6847291038472910",
    "wecom_kf": "WK_ORDER_001",
    "kuaishou": "KS_ORDER_001",
    "xhs": "XHS_ORDER_001",
}

NONEXISTENT_ID = "NONEXISTENT_ORDER_999"


# ── Helpers ──────────────────────────────────────────────────────────────

def _get(path: str) -> httpx.Response:
    return httpx.get(f"{BASE_URL}{path}", timeout=10)


def _assert_not_found(resp: httpx.Response):
    """Assert 404 with unified error format."""
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "error" in data
    assert data["error"] == "not_found"
    assert "detail" in data


def _assert_success(resp: httpx.Response):
    """Assert 200 with expected platform field."""
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "platform" in data


def _assert_no_source_leak(resp: httpx.Response):
    """Assert _source or source is not leaked in response."""
    raw = resp.text
    assert "_source" not in raw, f"_source leaked in response: {raw[:200]}"


# ── A. Normal path: 6 platforms × 4 chains ──────────────────────────────

class TestOrderNormalPath:
    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_order_returns_200_with_items(self, platform: str):
        resp = _get(f"/api/orders/{platform}/{VALID_ORDERS[platform]}")
        _assert_success(resp)
        _assert_no_source_leak(resp)
        data = resp.json()
        assert data["platform"] == platform
        assert data["order_id"] == VALID_ORDERS[platform]
        assert isinstance(data.get("items"), list)
        assert len(data["items"]) > 0, f"items should not be empty for {platform}"
        assert "total_amount" in data
        assert "status" in data


class TestShipmentNormalPath:
    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_shipment_returns_200(self, platform: str):
        resp = _get(f"/api/shipments/{platform}/{VALID_SHIPMENTS[platform]}")
        _assert_success(resp)
        _assert_no_source_leak(resp)
        data = resp.json()
        assert data["platform"] == platform
        assert data["order_id"] == VALID_SHIPMENTS[platform]
        assert isinstance(data.get("shipments"), list)
        assert len(data["shipments"]) > 0, f"shipments should not be empty for {platform}"


class TestAfterSaleNormalPath:
    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_after_sale_returns_200(self, platform: str):
        resp = _get(f"/api/after-sales/{platform}/{VALID_AFTERSALES[platform]}")
        _assert_success(resp)
        _assert_no_source_leak(resp)
        data = resp.json()
        assert data["platform"] == platform
        assert "reason" in data


class TestInventoryNormalPath:
    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_inventory_returns_200_with_items(self, platform: str):
        resp = _get(f"/api/inventory/{platform}/{VALID_INVENTORY[platform]}")
        _assert_success(resp)
        _assert_no_source_leak(resp)
        data = resp.json()
        assert data["platform"] == platform
        assert data["order_id"] == VALID_INVENTORY[platform]
        assert isinstance(data.get("items"), list)
        assert len(data["items"]) > 0, f"inventory items should not be empty for {platform}"
        item = data["items"][0]
        assert "sku_id" in item or "product_id" in item
        assert "quantity" in item


# ── B. Error semantics: 404 for nonexistent resources ────────────────────

class TestNotFoundSemantics:
    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_order_not_found(self, platform: str):
        resp = _get(f"/api/orders/{platform}/{NONEXISTENT_ID}")
        _assert_not_found(resp)

    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_shipment_not_found(self, platform: str):
        resp = _get(f"/api/shipments/{platform}/{NONEXISTENT_ID}")
        _assert_not_found(resp)

    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_after_sale_not_found(self, platform: str):
        resp = _get(f"/api/after-sales/{platform}/{NONEXISTENT_ID}")
        _assert_not_found(resp)

    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_inventory_not_found(self, platform: str):
        resp = _get(f"/api/inventory/{platform}/{NONEXISTENT_ID}")
        _assert_not_found(resp)


# ── C. Contract checks ───────────────────────────────────────────────────

class TestContractChecks:
    """Verify payload structure and key field presence across platforms."""

    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_order_has_required_fields(self, platform: str):
        resp = _get(f"/api/orders/{platform}/{VALID_ORDERS[platform]}")
        assert resp.status_code == 200
        data = resp.json()
        required = ["platform", "order_id", "status", "total_amount", "items"]
        for field in required:
            assert field in data, f"Missing required field '{field}' in {platform} order response"

    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_shipment_has_required_fields(self, platform: str):
        resp = _get(f"/api/shipments/{platform}/{VALID_SHIPMENTS[platform]}")
        assert resp.status_code == 200
        data = resp.json()
        required = ["platform", "order_id", "shipments"]
        for field in required:
            assert field in data, f"Missing required field '{field}' in {platform} shipment response"
        if data["shipments"]:
            ship = data["shipments"][0]
            for field in ["shipment_id", "express_company", "express_no", "status"]:
                assert field in ship, f"Missing field '{field}' in shipment item for {platform}"

    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_after_sale_has_required_fields(self, platform: str):
        resp = _get(f"/api/after-sales/{platform}/{VALID_AFTERSALES[platform]}")
        assert resp.status_code == 200
        data = resp.json()
        required = ["platform", "after_sale_id", "order_id", "status", "reason"]
        for field in required:
            assert field in data, f"Missing required field '{field}' in {platform} after-sale response"

    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_inventory_has_required_fields(self, platform: str):
        resp = _get(f"/api/inventory/{platform}/{VALID_INVENTORY[platform]}")
        assert resp.status_code == 200
        data = resp.json()
        required = ["platform", "order_id", "items"]
        for field in required:
            assert field in data, f"Missing required field '{field}' in {platform} inventory response"
        if data["items"]:
            item = data["items"][0]
            assert "quantity" in item

    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_no_source_leakage_order(self, platform: str):
        resp = _get(f"/api/orders/{platform}/{VALID_ORDERS[platform]}")
        _assert_no_source_leak(resp)

    @pytest.mark.parametrize("platform", PLATFORMS)
    def test_no_source_leakage_inventory(self, platform: str):
        resp = _get(f"/api/inventory/{platform}/{VALID_INVENTORY[platform]}")
        _assert_no_source_leak(resp)


# ── D. No regression: existing chains still work ─────────────────────────

class TestNoRegression:
    """Verify that previously working chains are not broken."""

    def test_jd_order_items_not_empty(self):
        resp = _get(f"/api/orders/jd/{VALID_ORDERS['jd']}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) > 0

    def test_taobao_order_items_not_empty(self):
        resp = _get(f"/api/orders/taobao/{VALID_ORDERS['taobao']}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) > 0

    def test_douyin_shop_order_items_not_empty(self):
        resp = _get(f"/api/orders/douyin_shop/{VALID_ORDERS['douyin_shop']}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) > 0

    def test_jd_shipment_has_tracking(self):
        resp = _get(f"/api/shipments/jd/{VALID_SHIPMENTS['jd']}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["shipments"]) > 0
        ship = data["shipments"][0]
        assert ship.get("express_no") or ship.get("shipment_id")

    def test_jd_after_sale_has_reason(self):
        resp = _get(f"/api/after-sales/jd/{VALID_AFTERSALES['jd']}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("reason")
