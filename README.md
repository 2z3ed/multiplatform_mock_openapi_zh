# Omni-CSX V2

Omni-CSX V2 是在 V1 稳定基线之上继续演进的多平台智能客服运营中台。

V1 聚焦“多平台统一接待 + 统一订单/物流/售后上下文 + AI 建议回复 + 人工确认发送”；  
V2 在此基础上继续补齐推荐、跟单、客户标签与画像、运营任务、统计分析、风险提醒等运营中台能力。:contentReference[oaicite:2]{index=2}

---

## 项目定位

Omni-CSX 不是单点聊天机器人，而是一个面向电商、私域、多平台接待场景的多平台智能客服运营中台。

项目要解决的核心问题包括：

- 平台分散
- 数据分散
- 知识分散
- 订单 / 物流 / 售后查询分散
- 客服重复劳动多
- 运营、客服、风控、业务系统之间断裂

因此，项目目标不是“让 AI 会聊天”，而是把多平台消息、订单、物流、售后、知识库、AI 建议回复和后续运营能力统一到一个中台中。

---

## V2 范围

V2 当前围绕以下能力展开：

- Recommendation（推荐记录与人工确认）
- Followup（跟单任务）
- Customer Tags（客户标签）
- Customer Profile（客户画像）
- Operation / Campaign（运营任务最小闭环）
- Analytics（统计摘要最小闭环）
- Risk Flags（风险标记最小闭环）

V2 延续“小模块完整闭环”的推进方式：

```text
design -> model + migration -> repository -> service -> API -> tests -> frontend
当前项目状态

当前项目阶段可以概括为：

V1 已完成并可冻结为 v1.0.0 稳定基线
V2 后端 7 个 MVP 模块已落地
V2 Frontend Phase 1 已完成最小前端能力
Agent Console 已具备会话详情增强 Panel 与独立页
Admin Console 已具备首页最小导航与只读验证页面
/analytics 页面已通过当前阶段验收：页面不再报错，当前可展示 2026-03-28 与 2026-03-29 两天的演示统计数据

注意：

当前前端实现以“最小可验证闭环”为主，不代表已经具备完整商用后台能力。
例如复杂 dashboard、图表中心、权限系统、完整后台运营体系仍不在当前范围内。

本地开发启动
前置要求
Python 3.11+
Node.js 20+
Docker & Docker Compose
pnpm workspace
启动步骤
安装依赖
# Python 依赖通过 pyproject.toml 管理
# 前端依赖通过 pnpm workspace 管理
启动数据库和缓存
docker compose up -d postgres redis
启动后端服务
docker compose up -d api-gateway domain-service ai-orchestrator knowledge-service mock-platform-server
启动前端服务
docker compose up -d agent-console admin-console
如需重新加载环境变量或镜像变更
docker compose up -d --force-recreate ai-orchestrator
docker compose up -d --force-recreate agent-console admin-console
验证服务
# API Gateway
curl http://localhost:8000/health

# Domain Service
curl http://localhost:8001/health

# AI Orchestrator
curl http://localhost:8002/health

# Knowledge Service
curl http://localhost:8003/health

# Mock Platform Server
curl http://localhost:8004/health
环境变量

关键环境变量在 .env 文件中配置：

POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=omni_csx
POSTGRES_USER=omni
POSTGRES_PASSWORD=omni

REDIS_HOST=redis
REDIS_PORT=6379

DATABASE_URL=postgresql+psycopg://omni:omni@postgres:5432/omni_csx

OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=your_base_url_if_needed
OPENAI_MODEL=your_model_name

说明：

有 OPENAI_API_KEY 时，AI Orchestrator 可接真实模型
无该变量时，可退回 Mock 模型
前端与后端都依赖数据库、缓存和 API Gateway 正常可用
服务入口
API Gateway: http://localhost:8000
Domain Service: http://localhost:8001
AI Orchestrator: http://localhost:8002
Knowledge Service: http://localhost:8003
Mock Platform Server: http://localhost:8004
Agent Console: http://localhost:3100
Admin Console: http://localhost:3200
核心 API
V1 核心 API
功能	API
会话列表	GET /api/conversations
会话详情	GET /api/conversations/{id}
消息列表	GET /api/conversations/{id}/messages
订单查询	GET /api/orders/{platform}/{orderId}
物流查询	GET /api/shipments/{platform}/{orderId}
AI 建议回复	POST /api/ai/suggest-reply
审计日志	GET/POST /api/audit-logs
文档上传	POST /api/kb/documents
重建索引	POST /api/kb/reindex
V2 当前前端依赖的主要 API
功能	API
Followup 列表	GET /api/follow-up/tasks
Followup execute	POST /api/follow-up/tasks/{id}/execute
Followup close	POST /api/follow-up/tasks/{id}/close
Recommendation 列表	GET /api/conversations/{id}/recommendations
Recommendation accept	POST /api/recommendations/{id}/accept
Recommendation reject	POST /api/recommendations/{id}/reject
Risk Flags 列表	GET /api/risk-flags?customer_id=
Risk Flag 创建	POST /api/risk-flags
Risk Flag resolve	POST /api/risk-flags/{id}/resolve
Risk Flag dismiss	POST /api/risk-flags/{id}/dismiss
Customer Profile	GET /api/customers/{customer_id}/profile
Customer Tags 列表	GET /api/customers/{customer_id}/tags
Tag 创建	POST /api/tags
Tag 删除	DELETE /api/tags/{id}
Operation 列表	GET /api/operation-campaigns
Analytics 摘要	GET /api/analytics/summaries?start_date=&end_date=
V2 已实现模块
后端
 Recommendation
 Followup
 Customer Tags
 Customer Profile
 Operation / Campaign
 Analytics
 Risk Flags
Agent Console 前端
 会话详情页增强 Panel
 FollowupPanel
 RecommendationPanel
 RiskFlagPanel
 CustomerProfilePanel
 独立页面
 /followups
 /operations
 /analytics
Admin Console 前端
 首页最小导航入口
 /operations
 /analytics
当前前端验收入口
Agent Console
/conversations
/conversations/conv_001
/conversations/conv_002
/followups
/operations
/analytics
会话详情页可验证面板
FollowupPanel
RecommendationPanel
RiskFlagPanel
CustomerProfilePanel
Admin Console
/
/operations
/analytics
/analytics 页面说明

/analytics 当前定位是“统计摘要只读页”，不是完整图表 dashboard。

当前页面要求：

只做 summaries 列表展示
不自动触发 POST summarize
前端默认请求最近 7 天数据
页面应具备以下四种状态：
loading
empty
error
normal
无历史数据时显示“暂无统计数据”
不扩展为 dashboard、图表中心、复杂分析页
当前验收结果

当前 /analytics 已通过当前阶段验收：

页面可以成功打开
/api/analytics/summaries?start_date=...&end_date=... 返回 200
backend GET /api/analytics/summaries?... 返回 200
当前页面已从 empty 进入 normal，可展示 2 行演示数据
当前不自动调用 summarize
当前不扩展为 dashboard / chart / summarize 按钮
当前演示数据说明

为了让 /analytics 页面在本地验收环境中展示正常统计行，当前通过本地 seed SQL 注入了 2 天演示数据：

2026-03-28
2026-03-29

对应字段示例：

2026-03-28
recommendation_created_count: 3
recommendation_accepted_count: 1
followup_executed_count: 2
followup_closed_count: 1
operation_campaign_completed_count: 1
2026-03-29
recommendation_created_count: 2
recommendation_accepted_count: 1
followup_executed_count: 1
followup_closed_count: 1
operation_campaign_completed_count: 0

说明：

这批数据属于本地演示 / 验收数据
用于让 /analytics 页面从 empty 进入 normal
当前不是正式统计回填链路
正式环境不应依赖这份 seed 数据作为业务统计来源
当前演示数据文件

当前本地演示数据通过以下 SQL 文件注入：

infra/migrations/0019_seed_analytics_summary.sql

建议在文件头部注明用途：

local demo only
acceptance only
not for production analytics generation
当前合理空状态 / 非阻塞项

以下情况在当前阶段属于合理状态，不应一律视为 bug：

非电商样本会话展示为空状态
某些平台暂不支持物流查询时显示“当前平台暂不支持物流查询”
/analytics 在无历史数据时显示空状态
Admin Console 当前只有最小导航入口和只读页，不代表缺失完整后台就是 bug
当前不在 V2 已完成范围内的内容

以下内容当前不应写成“已上线”：

完整 dashboard / 图表中心
更复杂的后台管理系统
权限系统
自动推荐引擎
个性化排序
自动运营编排
完整 ERP / OMS / WMS 深度联动
完整质检中心
完整风控中心
VOC 分析中心
培训中心
Deep Agents 主链路
自动发送回复
SaaS 多租户体系
V1 / V2 / V3 边界说明
V1

V1 仅包含以下三个核心能力：

多平台统一客服接入
统一订单 / 物流 / 售后上下文
AI 建议回复 + 人工确认后发送
V2

V2 在 V1 基础上继续补齐：

推荐
跟单
客户标签
客户画像
运营任务
统计摘要
风险标记
V3

V3 仍属于后续规划方向，主要包括：

质检中心
风控中心
ERP / OMS / WMS 深度联动
VOC / 管理分析 / 训练中心
目录结构
.
├── apps/
│   ├── api-gateway/           # 统一 API 入口
│   ├── domain-service/        # 业务主干服务
│   ├── ai-orchestrator/       # AI 工作流编排
│   ├── knowledge-service/     # 知识库服务
│   ├── mock-platform-server/  # 平台 Mock 服务
│   ├── agent-console/         # 客服工作台前端
│   └── admin-console/         # 管理后台前端
├── packages/
│   ├── domain-models/         # 统一领域模型
│   ├── provider-sdk/          # Provider SDK
│   ├── shared-config/         # 共享配置
│   ├── shared-db/             # 共享数据库能力
│   ├── shared-utils/          # 共享工具
│   └── shared-openapi/        # 共享 OpenAPI 产物
├── providers/
│   ├── jd/
│   │   ├── mock/
│   │   └── real/
│   ├── douyin_shop/
│   │   ├── mock/
│   │   └── real/
│   └── wecom_kf/
│       ├── mock/
│       └── real/
├── infra/
│   ├── docker/
│   ├── migrations/
│   └── scripts/
├── docs/
├── tests/
└── .ai/
    └── v2/
核心服务职责
api-gateway

统一 API 入口，负责：

统一对外路由
鉴权 / 中间件
request_id / 访问日志
对前端暴露统一接口
domain-service

业务主干服务，负责：

conversations
messages
orders
shipments
after-sales
recommendation
followup
customer tags
customer profile
operation / campaign
analytics
risk flags
ai-orchestrator

AI 子系统与工作流，负责：

intent_chain
suggest_reply_chain
tools
suggest_reply_graph
后续 recommendation / followup / campaign 等 AI 工作流扩展
knowledge-service

知识库服务，负责：

文档上传
文档切片
embedding
retrieval
mock-platform-server

平台 mock 服务，负责：

provider mock 接口
本地开发与联调支撑
Mock First 开发流程
agent-console

客服工作台，负责：

会话列表
会话详情
会话详情增强 Panel
/followups
/operations
/analytics
admin-console

管理后台，负责：

首页最小导航入口
/operations
/analytics
工程规则

当前项目遵循以下工程规则：

坚持 Mock First
坚持 Provider Pattern
坚持统一领域模型
AI 只作为子系统，不承担整个项目主框架
V1 主链路不允许 AI 自动发送
AI 输出必须结构化
审计日志应记录关键写操作
开发顺序固定：
schema / database
repository
service
API
OpenAPI
tests
frontend
一次只推进一个模块
每个模块都尽量形成完整闭环
Git / 分支策略

当前推荐策略如下：

main：稳定主分支
v1.0.0：V1 基线标签
v2-dev：V2 开发分支

建议做法：

保持 V1 基线干净
所有 V2 开发继续在 v2-dev 上推进
不把 V2 / V3 能力泄漏回 V1
当前阶段总结

当前 Omni-CSX 的真实状态可以概括为：

V1 已完成并可冻结
V2 backend 7 个 MVP 模块已完成
V2 Frontend Phase 1 已完成
Agent Console 已具备最小可验收页面与 Panel
Admin Console 已具备最小可验收页面
/analytics 页面已通过当前阶段验收，并可展示 2 天本地演示统计数据
当前重点是页面与真实 API 的进一步验收对齐，以及逐步把演示能力过渡到更真实的业务数据链路