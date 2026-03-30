# Omni-CSX V1 Agent Instructions

## 1. Project Goal

This repository is for V1 of Omni-CSX.

V1 only does three things:
- multi-platform unified customer service intake
- unified order / shipment / after-sale context
- AI suggested reply with human confirmation before send

Anything outside these three goals is out of scope for V1.

## 2. V1 Out of Scope

Do NOT implement in V1:
- recommendation engine
- customer profiling
- marketing tasks
- campaign system
- quality inspection center
- risk center
- ERP deep integration
- VOC analysis
- training center
- Deep Agents
- automatic reply sending
- SaaS multi-tenant features

## 3. Required Tech Stack

Backend:
- FastAPI
- PostgreSQL
- Redis

AI:
- LangChain
- LangGraph

Frontend:
- Next.js
- React

## 4. Framework Responsibilities

### FastAPI
FastAPI is the primary backend framework.
Use FastAPI for:
- all REST APIs
- webhook endpoints
- admin APIs
- platform config APIs
- audit log APIs
- background task triggers
- OpenAPI generation

Do NOT use LangGraph for:
- CRUD
- provider config
- webhook handling
- admin backend
- normal service logic

### LangChain
Use LangChain only for:
- model abstraction
- tool calling
- retrieval integration
- structured output
- prompt composition
- suggested reply generation

### LangGraph
Use LangGraph only for:
- suggest_reply_graph

Do NOT use LangGraph outside the AI workflow layer.

### Deep Agents
Deep Agents are forbidden in V1.
They may only be reconsidered in V3 for side-path analysis tasks.

## 5. Required Architecture

All platform integrations must follow:

business layer
-> provider-sdk interface
-> provider implementation
-> mock / real switch

Each platform provider must have:
- mock implementation
- real implementation skeleton

V1 only implements mock behavior.
Real providers may remain placeholders.

Do NOT bypass provider-sdk.

## 6. Mock First Rule

All external platform integrations in V1 must first go through mock-platform-server.

Correct order:
official contract
-> mock platform API
-> provider adapter
-> unified domain service
-> AI and frontend

Never skip platform abstraction because a real API key is unavailable.

## 7. Unified Domain Model Rule

All platform-specific data must be mapped into unified objects before use.

Required unified objects:
- Customer
- Conversation
- Message
- Order
- Shipment
- AfterSaleCase
- AISuggestion
- AuditLog

Platform-specific raw payloads may only go into:
- raw_json
- extra_json

Do not expose platform raw JSON directly to frontend or AI layers.

## 8. AI Behavior Rule

For order / shipment / after-sale requests:
- AI must call tools first
- AI must not answer from free-form generation alone

For FAQ / SOP:
- AI must retrieve knowledge first

Required AI tools:
- get_order
- get_shipment
- get_after_sale
- search_kb

Required AI output fields:
- intent
- confidence
- suggested_reply
- used_tools
- risk_level

AI may only generate a suggested reply.
Final send must always be confirmed by a human agent.

## 9. Required LangGraph Workflow

There must be exactly one LangGraph workflow in V1:
- suggest_reply_graph

Required nodes:
- load_context
- classify_intent
- route_to_tool_or_kb
- build_prompt_context
- generate_suggestion
- human_review_interrupt

Do NOT create additional graphs in V1.

## 10. Required Services

The repository must contain:
- api-gateway
- domain-service
- ai-orchestrator
- knowledge-service
- mock-platform-server
- agent-console
- admin-console

## 11. Required Shared Packages

The repository must contain:
- domain-models
- provider-sdk
- shared-utils
- shared-config
- shared-db

## 12. Required Providers

The repository must contain:
- providers/jd/mock
- providers/jd/real
- providers/douyin_shop/mock
- providers/douyin_shop/real
- providers/wecom_kf/mock
- providers/wecom_kf/real

## 13. Required Database Tables

Minimum required tables:
- platform_account
- customer
- conversation
- message
- order_snapshot
- shipment_snapshot
- after_sale_case
- kb_document
- kb_chunk
- ai_suggestion
- audit_log

Do NOT add V2/V3 tables in V1.

## 14. Required APIs

### Mock platform APIs

JD:
- POST /mock/jd/oauth/token
- GET /mock/jd/orders/{orderId}
- GET /mock/jd/shipments/{orderId}
- GET /mock/jd/after-sales/{afterSaleId}

Douyin Shop:
- POST /mock/douyin-shop/auth/token
- GET /mock/douyin-shop/orders/{orderId}
- GET /mock/douyin-shop/refunds/{afterSaleId}
- GET /mock/douyin-shop/products/{productId}

WeCom KF:
- POST /mock/wecom-kf/token
- POST /mock/wecom-kf/messages/sync
- POST /mock/wecom-kf/service-state/trans
- POST /mock/wecom-kf/event-message/send

### Unified APIs

Conversation:
- GET /api/conversations
- GET /api/conversations/{id}
- GET /api/conversations/{id}/messages
- POST /api/conversations/{id}/assign
- POST /api/conversations/{id}/handoff

Context:
- GET /api/orders/{platform}/{orderId}
- GET /api/shipments/{platform}/{orderId}
- GET /api/after-sales/{platform}/{afterSaleId}

AI:
- POST /api/ai/suggest-reply

Knowledge:
- POST /api/kb/documents
- POST /api/kb/reindex
- GET /api/kb/search

Audit:
- GET /api/audit-logs

## 15. Required Frontend Pages

### Agent console
Allowed pages:
- /login
- /conversations
- /conversations/[id]

Conversation detail page must include:
- ConversationHeader
- MessageStream
- ReplyComposer
- OrderPanel
- ShipmentPanel
- AfterSalePanel
- SuggestionPanel

### Admin console
Allowed pages:
- /platforms
- /knowledge
- /audit

Do NOT create V2/V3 pages in V1.

## 16. Audit Logging Rule

The following actions must always create audit logs:
- platform config updated
- provider mode switched
- document uploaded
- knowledge reindexed
- AI suggestion generated
- agent message sent
- conversation handed off
- conversation assigned

Any feature without audit logging is incomplete.

## 17. OpenAPI Rule

Every backend service must expose OpenAPI.

Every important route must include:
- request schema
- response schema
- validation
- error handling

## 18. Testing Rule

Every new feature must include:
- at least one service-level test
- at least one API-level test

Required integration tests:
- mock flow
- provider switch flow
- conversation -> AI suggestion flow

No tests means not complete.

## 19. Development Order

Always implement in this order:
- schema / database
- repository
- service
- API
- OpenAPI
- tests
- frontend

Never start from UI-first implementation.

## 20. Directory Responsibility Rule

api-gateway:
- unified entry and routing only

domain-service:
- unified business entities and domain logic only

ai-orchestrator:
- AI chains, tools, graph, suggestion workflow only

knowledge-service:
- document ingest, chunking, embedding, retrieval only

mock-platform-server:
- platform simulation only

agent-console:
- agent workbench UI only

admin-console:
- admin/configuration UI only

Do not mix responsibilities across services.

## 21. Naming Rule

Use:
- snake_case for Python files
- snake_case for DB tables
- PascalCase for React components
- consistent REST naming
- DTO / schema names aligned with unified domain model names

## 22. Simplicity Rule

Choose the simplest valid implementation for V1.
Do not add speculative abstractions.
Do not add future business logic.
Leave future modules as placeholders only if necessary.

## 23. Definition of Done

V1 is done only when:
- all required services run locally
- all required DB tables exist
- all required mock routes are callable
- unified APIs work
- knowledge upload and retrieval work
- AI suggested reply works through the graph flow
- human can review and send the reply
- provider mode can switch
- audit logs are visible
- required tests pass