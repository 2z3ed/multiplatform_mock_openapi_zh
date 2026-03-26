"""
Integration tests for V1

Tests:
1. Mock platform route flow
2. Provider mapping flow
3. Conversation -> AI suggestion flow
4. Provider mode switch flow
"""

import pytest
import httpx
import asyncio


BASE_URL = "http://localhost:8000"
MOCK_SERVER_URL = "http://localhost:8004"
DOMAIN_SERVICE_URL = "http://localhost:8001"
AI_ORCHESTRATOR_URL = "http://localhost:8002"
KNOWLEDGE_SERVICE_URL = "http://localhost:8003"


class TestMockPlatformRoutes:
    """Test mock platform server routes"""

    @pytest.mark.asyncio
    async def test_jd_oauth_token(self):
        """Test JD OAuth token endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{MOCK_SERVER_URL}/mock/jd/oauth/token")
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data

    @pytest.mark.asyncio
    async def test_jd_get_order(self):
        """Test JD get order endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MOCK_SERVER_URL}/mock/jd/orders/JD20240315001")
            assert response.status_code == 200
            data = response.json()
            assert data["orderId"] == "JD20240315001"

    @pytest.mark.asyncio
    async def test_douyin_shop_auth_token(self):
        """Test Douyin Shop auth token endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{MOCK_SERVER_URL}/mock/douyin-shop/auth/token")
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data

    @pytest.mark.asyncio
    async def test_wecom_kf_token(self):
        """Test WeCom KF token endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{MOCK_SERVER_URL}/mock/wecom-kf/token")
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data


class TestProviderMapping:
    """Test provider mapping from mock platform to DTO"""

    @pytest.mark.asyncio
    async def test_jd_order_mapping(self):
        """Test JD order is correctly mapped"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DOMAIN_SERVICE_URL}/api/orders/jd/JD20240315001")
            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "jd"
            assert "status" in data
            assert "items" in data

    @pytest.mark.asyncio
    async def test_jd_shipment_mapping(self):
        """Test JD shipment is correctly mapped"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DOMAIN_SERVICE_URL}/api/shipments/jd/JD20240315001")
            assert response.status_code == 200
            data = response.json()
            assert data["platform"] == "jd"
            assert "shipments" in data


class TestConversationFlow:
    """Test conversation and context flow"""

    @pytest.mark.asyncio
    async def test_list_conversations(self):
        """Test listing conversations"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DOMAIN_SERVICE_URL}/api/conversations")
            assert response.status_code == 200
            data = response.json()
            assert "items" in data

    @pytest.mark.asyncio
    async def test_get_conversation_messages(self):
        """Test getting conversation messages"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{DOMAIN_SERVICE_URL}/api/conversations/conv_001/messages")
            assert response.status_code == 200
            data = response.json()
            assert "items" in data


class TestAISuggestionFlow:
    """Test AI suggestion flow"""

    @pytest.mark.asyncio
    async def test_suggest_reply_with_order_query(self):
        """Test AI suggests reply for order query"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_ORCHESTRATOR_URL}/api/ai/suggest-reply",
                json={
                    "conversation_id": "conv_001",
                    "message": "我想查询订单状态",
                    "platform": "jd"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "intent" in data
            assert "suggested_reply" in data
            assert data["needs_human_review"] is True

    @pytest.mark.asyncio
    async def test_suggest_reply_with_faq(self):
        """Test AI suggests reply for FAQ"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{AI_ORCHESTRATOR_URL}/api/ai/suggest-reply",
                json={
                    "conversation_id": "conv_001",
                    "message": "如何查询订单？",
                    "platform": "jd"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "intent" in data
            assert data["intent"] in ["faq", "order_query"]


class TestKnowledgeService:
    """Test knowledge service"""

    @pytest.mark.asyncio
    async def test_upload_document(self):
        """Test uploading document"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{KNOWLEDGE_SERVICE_URL}/api/kb/documents",
                json={
                    "title": "测试FAQ",
                    "content": "如何查询订单. 请在订单页面查看. 退货流程是先申请.",
                    "doc_type": "faq"
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "document_id" in data
            assert data["chunk_count"] > 0

    @pytest.mark.asyncio
    async def test_search_knowledge(self):
        """Test searching knowledge"""
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{KNOWLEDGE_SERVICE_URL}/api/kb/documents",
                json={
                    "title": "测试FAQ",
                    "content": "如何查询订单. 请在订单页面查看.",
                    "doc_type": "faq"
                }
            )
            response = await client.post(
                f"{KNOWLEDGE_SERVICE_URL}/api/kb/search",
                json={"query": "订单", "top_k": 5}
            )
            assert response.status_code == 200
            data = response.json()
            assert "results" in data


class TestHealth:
    """Test service health endpoints"""

    @pytest.mark.asyncio
    async def test_api_gateway_health(self):
        """Test API Gateway health"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_mock_platform_health(self):
        """Test Mock Platform Server health"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MOCK_SERVER_URL}/health")
            assert response.status_code == 200


class TestAuditLogPersistence:
    """Test audit log persistence end-to-end"""

    @pytest.mark.asyncio
    async def test_audit_log_persists_after_creation(self):
        """Test that audit log is persisted to database after creation"""
        async with httpx.AsyncClient() as client:
            create_response = await client.post(
                f"{DOMAIN_SERVICE_URL}/api/audit-logs",
                json={
                    "action": "message_sent",
                    "actor_type": "agent",
                    "actor_id": "agent_test",
                    "target_type": "conversation",
                    "target_id": "conv_e2e_test",
                    "detail": "End-to-end test message"
                }
            )
            assert create_response.status_code == 200
            created_log = create_response.json()
            assert created_log["status"] == "ok"
            assert "log" in created_log
            log_id = created_log["log"]["id"]
            assert log_id is not None

            get_response = await client.get(f"{DOMAIN_SERVICE_URL}/api/audit-logs?limit=100")
            assert get_response.status_code == 200
            data = get_response.json()
            assert "items" in data
            found = any(item["id"] == log_id for item in data["items"])
            assert found, f"Created audit log with id {log_id} not found in database"

    @pytest.mark.asyncio
    async def test_conversation_assign_creates_audit_log(self):
        """Test that assigning conversation creates audit log"""
        async with httpx.AsyncClient() as client:
            before_response = await client.get(f"{DOMAIN_SERVICE_URL}/api/audit-logs?limit=100")
            before_count = len(before_response.json()["items"])

            assign_response = await client.post(
                f"{DOMAIN_SERVICE_URL}/api/conversations/conv_001/assign",
                params={"agent_id": "agent_test_assign"}
            )
            assert assign_response.status_code == 200

            after_response = await client.get(f"{DOMAIN_SERVICE_URL}/api/audit-logs?limit=100")
            after_data = after_response.json()
            after_count = len(after_data["items"])

            assert after_count > before_count
            conv_assign_logs = [l for l in after_data["items"] if l.get("action") == "conversation_assigned"]
            assert len(conv_assign_logs) > 0

    @pytest.mark.asyncio
    async def test_ai_suggestion_to_human_send_flow(self):
        """Test full flow: conversation -> AI suggestion -> human send -> audit log"""
        async with httpx.AsyncClient() as client:
            before_response = await client.get(f"{DOMAIN_SERVICE_URL}/api/audit-logs?limit=100")
            before_count = len(before_response.json()["items"])

            ai_response = await client.post(
                f"{AI_ORCHESTRATOR_URL}/api/ai/suggest-reply",
                json={
                    "conversation_id": "conv_001",
                    "message": "我想查询订单状态",
                    "platform": "jd"
                }
            )
            assert ai_response.status_code == 200
            ai_data = ai_response.json()
            assert "suggested_reply" in ai_data

            send_response = await client.post(
                f"{DOMAIN_SERVICE_URL}/api/audit-logs",
                json={
                    "action": "message_sent",
                    "actor_type": "agent",
                    "actor_id": "agent_001",
                    "target_type": "message",
                    "target_id": f"msg_{int(asyncio.get_event_loop().time() * 1000)}",
                    "detail": "Sent message in conversation: conv_001",
                    "detail_json": {
                        "conversation_id": "conv_001",
                        "content": ai_data["suggested_reply"]
                    }
                }
            )
            assert send_response.status_code == 200

            after_response = await client.get(f"{DOMAIN_SERVICE_URL}/api/audit-logs?limit=100")
            after_data = after_response.json()
            after_count = len(after_data["items"])

            assert after_count > before_count
            msg_sent_logs = [l for l in after_data["items"] if l.get("action") == "message_sent"]
            assert len(msg_sent_logs) > 0