import pytest
from httpx import AsyncClient, ASGITransport
from apps.knowledge_service.app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestKnowledgeService:
    @pytest.mark.asyncio
    async def test_upload_document(self, client):
        response = await client.post("/api/kb/documents", json={
            "title": "测试FAQ",
            "content": "如何查询订单. 请在订单页面查看. 退货流程是先申请.",
            "doc_type": "faq"
        })
        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["title"] == "测试FAQ"
        assert data["chunk_count"] > 0

    @pytest.mark.asyncio
    async def test_reindex(self, client):
        response = await client.post("/api/kb/reindex")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_search(self, client):
        await client.post("/api/kb/documents", json={
            "title": "测试FAQ",
            "content": "如何查询订单. 请在订单页面查看.",
            "doc_type": "faq"
        })
        response = await client.post("/api/kb/search", json={
            "query": "订单",
            "top_k": 5
        })
        assert response.status_code == 200
        data = response.json()
        assert "results" in data


class TestHealth:
    @pytest.mark.asyncio
    async def test_health(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "knowledge-service"