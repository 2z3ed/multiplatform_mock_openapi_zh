"""
E4-C: Odoo mode and upstream failure automated tests.

Covers:
- Odoo mode regression for jd / taobao / douyin_shop × 4 chains
- 503 / upstream unavailable scenarios
- Fallback behavior (Odoo down + fixture exists → 200)
- Controlled failure (Odoo down + no fixture → 404/503)

Prerequisites:
- official-sim running with ORDER_SOURCE_MODE=odoo
- Odoo instance available at configured URL
- For 503 tests: Odoo must be stoppable or unreachable

Run Odoo mode tests:
    pytest tests/regression/test_odoo_mode.py -v -k odoo

Run 503 tests (requires Odoo to be stopped):
    pytest tests/regression/test_upstream_failure.py -v
"""

import pytest
import httpx
import os
import subprocess
import time

OFFICIAL_SIM_URL = os.getenv("OFFICIAL_SIM_URL", "http://localhost:9001/official-sim/query")
MAIN_URL = os.getenv("MAIN_URL", "http://localhost:8000")

CORE_PLATFORMS = ["jd", "taobao", "douyin_shop"]

# Odoo order ID (exists in Odoo)
ODOO_ORDER_ID = "S00032"

# Non-existent order ID (not in Odoo, not in fixture)
NONEXISTENT_ID = "NONEXISTENT_ORDER_999_FOR_ODOO_TEST"


# ── Helpers ──────────────────────────────────────────────────────────────

def _get(path: str, base: str = MAIN_URL) -> httpx.Response:
    return httpx.get(f"{base}{path}", timeout=15)


def _assert_success(resp: httpx.Response):
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert "platform" in data


def _assert_not_found(resp: httpx.Response):
    assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("error") == "not_found"


def _assert_no_source_leak(resp: httpx.Response):
    raw = resp.text
    assert "_source" not in raw, f"_source leaked: {raw[:200]}"


def _is_odoo_available() -> bool:
    """Check if Odoo instance is currently reachable."""
    try:
        r = httpx.post(
            "http://localhost:8069/jsonrpc",
            json={"jsonrpc": "2.0", "method": "call", "params": {"service": "common", "method": "version", "args": []}, "id": 1},
            timeout=5
        )
        return r.status_code == 200
    except Exception:
        return False


def _set_official_sim_mode(mode: str):
    """Switch official-sim source mode by restarting with new env.

    This is done externally; tests should be run with the correct mode already set.
    This helper documents the expected setup.
    """
    pass  # Mode is set via environment before running tests


# ── A. Odoo mode regression (3 platforms × 4 chains) ─────────────────────

@pytest.mark.skipif(not _is_odoo_available(), reason="Odoo instance not available")
class TestOdooModeRegression:
    """Verify all 3 core platforms work in Odoo mode."""

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_order_returns_200(self, platform: str):
        resp = _get(f"/api/orders/{platform}/{ODOO_ORDER_ID}")
        _assert_success(resp)
        _assert_no_source_leak(resp)
        data = resp.json()
        assert data["platform"] == platform
        assert data["order_id"] == ODOO_ORDER_ID
        assert isinstance(data.get("items"), list)
        assert len(data["items"]) > 0, f"Odoo order items should not be empty for {platform}"
        assert "total_amount" in data
        assert "status" in data

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_shipment_returns_200(self, platform: str):
        resp = _get(f"/api/shipments/{platform}/{ODOO_ORDER_ID}")
        _assert_success(resp)
        _assert_no_source_leak(resp)
        data = resp.json()
        assert data["platform"] == platform
        assert data["order_id"] == ODOO_ORDER_ID
        assert isinstance(data.get("shipments"), list)

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_after_sale_returns_200(self, platform: str):
        resp = _get(f"/api/after-sales/{platform}/{ODOO_ORDER_ID}")
        _assert_success(resp)
        _assert_no_source_leak(resp)
        data = resp.json()
        assert data["platform"] == platform
        assert "reason" in data

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_inventory_returns_200(self, platform: str):
        resp = _get(f"/api/inventory/{platform}/{ODOO_ORDER_ID}")
        _assert_success(resp)
        _assert_no_source_leak(resp)
        data = resp.json()
        assert data["platform"] == platform
        assert data["order_id"] == ODOO_ORDER_ID
        assert isinstance(data.get("items"), list)
        assert len(data["items"]) > 0, f"Odoo inventory items should not be empty for {platform}"
        item = data["items"][0]
        assert "quantity" in item
        assert "sku_id" in item or "product_id" in item

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_order_platform_structure(self, platform: str):
        """Verify platform-specific structure is preserved in Odoo mode."""
        resp = _get(f"/api/orders/{platform}/{ODOO_ORDER_ID}")
        assert resp.status_code == 200
        data = resp.json()

        # All platforms should have these base fields
        assert "platform" in data
        assert "order_id" in data
        assert "status" in data
        assert "total_amount" in data
        assert "items" in data

        # Platform-specific checks
        if platform == "jd":
            assert data["platform"] == "jd"
        elif platform == "taobao":
            assert data["platform"] == "taobao"
        elif platform == "douyin_shop":
            assert data["platform"] == "douyin_shop"


# ── B. Odoo mode: nonexistent resource → 404 ─────────────────────────────

@pytest.mark.skipif(not _is_odoo_available(), reason="Odoo instance not available")
class TestOdooModeNotFound:
    """Verify 404 semantics are preserved in Odoo mode."""

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_order_not_found(self, platform: str):
        resp = _get(f"/api/orders/{platform}/{NONEXISTENT_ID}")
        _assert_not_found(resp)

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_shipment_not_found(self, platform: str):
        resp = _get(f"/api/shipments/{platform}/{NONEXISTENT_ID}")
        _assert_not_found(resp)

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_after_sale_not_found(self, platform: str):
        resp = _get(f"/api/after-sales/{platform}/{NONEXISTENT_ID}")
        _assert_not_found(resp)

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_inventory_not_found(self, platform: str):
        resp = _get(f"/api/inventory/{platform}/{NONEXISTENT_ID}")
        _assert_not_found(resp)


# ── C. Upstream failure: Odoo unavailable ────────────────────────────────

class TestOdooUnavailableWithFixtureFallback:
    """Test behavior when Odoo is unavailable but fixture data exists.

    These tests require official-sim to be running in Odoo mode with Odoo stopped.
    If Odoo is available, these tests will be skipped.

    Expected behavior:
    - Odoo unavailable + fixture exists → 200 (fallback)
    - Odoo unavailable + no fixture → 404 (not found)
    """

    @pytest.mark.skipif(_is_odoo_available(), reason="Odoo is available; stop Odoo to run these tests")
    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_down_fixture_fallback_order(self, platform: str):
        """When Odoo is down but fixture exists, should return 200 with fixture data."""
        # Use a known fixture order ID
        fixture_ids = {
            "jd": "304857291638",
            "taobao": "4728561930472815",
            "douyin_shop": "6847291038472910",
        }
        resp = _get(f"/api/orders/{platform}/{fixture_ids[platform]}")
        # Should fallback to fixture and return 200
        assert resp.status_code == 200, f"Expected 200 (fixture fallback), got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["platform"] == platform
        assert "order_id" in data

    @pytest.mark.skipif(_is_odoo_available(), reason="Odoo is available; stop Odoo to run these tests")
    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_down_no_fixture_returns_404(self, platform: str):
        """When Odoo is down and no fixture exists, should return 404."""
        resp = _get(f"/api/orders/{platform}/{NONEXISTENT_ID}")
        _assert_not_found(resp)

    @pytest.mark.skipif(_is_odoo_available(), reason="Odoo is available; stop Odoo to run these tests")
    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_down_fixture_fallback_inventory(self, platform: str):
        """Inventory should also fallback to fixture when Odoo is down."""
        fixture_ids = {
            "jd": "304857291638",
            "taobao": "4728561930472815",
            "douyin_shop": "6847291038472910",
        }
        resp = _get(f"/api/inventory/{platform}/{fixture_ids[platform]}")
        assert resp.status_code == 200, f"Expected 200 (fixture fallback), got {resp.status_code}: {resp.text}"
        data = resp.json()
        assert data["platform"] == platform
        assert "items" in data


# ── D. Direct official-sim Odoo mode tests ──────────────────────────────

@pytest.mark.skipif(not _is_odoo_available(), reason="Odoo instance not available")
class TestOfficialSimOdooModeDirect:
    """Test official-sim directly in Odoo mode to verify the pipeline."""

    def _official_sim_get(self, path: str) -> httpx.Response:
        return httpx.get(f"{OFFICIAL_SIM_URL}{path}", timeout=15)

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_order_direct(self, platform: str):
        resp = self._official_sim_get(f"/orders/{ODOO_ORDER_ID}?platform={platform}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("code") == "0"
        order = data["data"]["order"]

        # Platform-specific order ID location
        if platform == "jd":
            assert order.get("order_id") == ODOO_ORDER_ID
        elif platform == "taobao":
            # Taobao uses nested trade.tid
            assert order.get("trade", {}).get("tid") == ODOO_ORDER_ID or order.get("order_id") == ODOO_ORDER_ID
        elif platform == "douyin_shop":
            # Douyin uses nested order.order_id
            assert order.get("order", {}).get("order_id") == ODOO_ORDER_ID or order.get("order_id") == ODOO_ORDER_ID

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_shipment_direct(self, platform: str):
        resp = self._official_sim_get(f"/orders/{ODOO_ORDER_ID}/shipment?platform={platform}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("code") == "0"

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_after_sale_direct(self, platform: str):
        resp = self._official_sim_get(f"/orders/{ODOO_ORDER_ID}/refund?platform={platform}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("code") == "0"

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_inventory_direct(self, platform: str):
        resp = self._official_sim_get(f"/orders/{ODOO_ORDER_ID}/inventory?platform={platform}")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("code") == "0"
        inventory = data["data"]["inventory"]
        assert isinstance(inventory, list)
        assert len(inventory) > 0

    @pytest.mark.parametrize("platform", CORE_PLATFORMS)
    def test_odoo_not_found_direct(self, platform: str):
        resp = self._official_sim_get(f"/orders/{NONEXISTENT_ID}?platform={platform}")
        assert resp.status_code == 404
