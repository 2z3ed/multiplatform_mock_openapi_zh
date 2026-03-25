import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestJDRoutes:
    @pytest.mark.asyncio
    async def test_oauth_token(self, client):
        response = await client.post("/mock/jd/oauth/token")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"

    @pytest.mark.asyncio
    async def test_get_order(self, client):
        response = await client.get("/mock/jd/orders/JD20240315001")
        assert response.status_code == 200
        data = response.json()
        assert data["orderId"] == "JD20240315001"
        assert "items" in data

    @pytest.mark.asyncio
    async def test_get_shipment(self, client):
        response = await client.get("/mock/jd/shipments/JD20240315001")
        assert response.status_code == 200
        data = response.json()
        assert "shipments" in data
        assert data["orderId"] == "JD20240315001"

    @pytest.mark.asyncio
    async def test_get_after_sale(self, client):
        response = await client.get("/mock/jd/after-sales/AS20240320001")
        assert response.status_code == 200
        data = response.json()
        assert data["afterSaleId"] == "AS20240320001"
        assert "type" in data


class TestDouyinShopRoutes:
    @pytest.mark.asyncio
    async def test_auth_token(self, client):
        response = await client.post("/mock/douyin-shop/auth/token")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "Bearer"

    @pytest.mark.asyncio
    async def test_get_order(self, client):
        response = await client.get("/mock/douyin-shop/orders/DY20240315001")
        assert response.status_code == 200
        data = response.json()
        assert data["orderId"] == "DY20240315001"
        assert "items" in data

    @pytest.mark.asyncio
    async def test_get_refund(self, client):
        response = await client.get("/mock/douyin-shop/refunds/REF20240320001")
        assert response.status_code == 200
        data = response.json()
        assert data["refundId"] == "REF20240320001"
        assert "type" in data

    @pytest.mark.asyncio
    async def test_get_product(self, client):
        response = await client.get("/mock/douyin-shop/products/PRD001")
        assert response.status_code == 200
        data = response.json()
        assert data["productId"] == "PRD001"
        assert "productName" in data


class TestWecomKFRoutes:
    @pytest.mark.asyncio
    async def test_token(self, client):
        response = await client.post("/mock/wecom-kf/token")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "corp_id" in data

    @pytest.mark.asyncio
    async def test_message_sync(self, client):
        response = await client.post("/mock/wecom-kf/messages/sync", json={"content": "test message"})
        assert response.status_code == 200
        data = response.json()
        assert "msgid" in data
        assert data["content"] == "test message"

    @pytest.mark.asyncio
    async def test_service_state_trans(self, client):
        response = await client.post("/mock/wecom-kf/service-state/trans", json={"service_state": "SERVING"})
        assert response.status_code == 200
        data = response.json()
        assert data["service_state"] == "SERVING"
        assert data["service_state_name"] == "服务中"

    @pytest.mark.asyncio
    async def test_event_message_send(self, client):
        response = await client.post("/mock/wecom-kf/event-message/send", json={"event_type": "kf_msg_sent"})
        assert response.status_code == 200
        data = response.json()
        assert data["event_type"] == "kf_msg_sent"


class TestHealth:
    @pytest.mark.asyncio
    async def test_health(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "mock-platform-server"