# Omni-CSX

Omni-CSX 是一个面向电商、私域、多平台接待场景的 **多平台智能客服运营中台**。

它不是单点 AI 聊天机器人，也不是单一知识库问答系统。  
它的目标是把分散在多个平台和多个系统中的：

- 消息
- 订单
- 物流
- 售后
- 知识库
- AI 建议回复
- 运营与分析能力

统一到一个中台中，形成“**统一接待 + 统一业务上下文 + AI 辅助处理 + 人工确认执行**”的工作模式。

---

## 当前仓库状态

当前仓库状态可以统一理解为：

- **V1 已完成并冻结**
- **V2 已完成并收口**
- **V3 MVP 已完成**
- **V3.5 已完成并封板**

这意味着当前仓库不是“开发中原型”，而是已经经历了：

- V1：客服中台底座
- V2：客服运营中台最小闭环
- V3：四个 Phase 的 MVP 闭环
- V3.5：真实 Odoo 接入强化阶段

当前 **V3.5 已完成全部既定范围并正式封板**。  
后续如果继续扩展，应视作新一轮阶段评审，而不是继续在 V3.5 范围内无边界扩写。

---

## 项目定位

Omni-CSX 要解决的核心问题不是“客服不会说”，而是：

- 平台分散
- 数据分散
- 知识分散
- 订单 / 物流 / 售后查询分散
- 客服重复劳动多
- 运营、客服、风控、业务系统之间断裂

因此，项目目标不是“做一个 AI 客服机器人”，而是建设一套：

> **多平台智能客服运营中台**

它的核心价值包括：

- 统一多平台客服入口
- 统一订单、物流、售后和知识库上下文
- 让 AI 帮客服查信息、组织回复、处理重复问题
- 降低重复劳动
- 提升客服人效
- 统一服务标准
- 为后续更多平台接入和业务自动化提供基础设施

一句话表达：

> 我们做的不是机器人，而是企业的多平台智能客服操作系统。

---

## 核心架构

项目采用：

> **中台 + Provider + AI Workflow + Snapshot**

### 核心原则

- **Mock First**
- **Provider Pattern**
- **Unified Domain Model**
- **Human-in-the-loop**
- 审计必写
- OpenAPI 必须可见
- tests 必须跟上
- 一次只推进一个模块
- backend 先于 frontend

### 架构思想

#### 1. Mock First
先做 mock provider，再接 real provider。  
即使暂时拿不到真实 API 权限，也不阻塞中台主干开发。

#### 2. Provider Pattern
每个平台都拆成 `mock / real` 两层，上层统一通过 provider-sdk 调用，不直接依赖平台原始字段。

#### 3. 统一领域模型
各平台数据统一映射为系统内部统一结构，例如：

- Customer
- Conversation
- Message
- Order
- Shipment
- AfterSaleCase
- AISuggestion
- AuditLog

#### 4. AI 只是子系统
AI 不承担整个项目主框架，只负责：

- 意图识别
- 工具调用
- 检索
- 建议回复
- 以及后续 recommendation / followup / risk / voc 等子流程

#### 5. Snapshot 作为中间层
尤其在 V3.5 里，真实 Odoo 数据不会直接透传给前端，而是遵循：

```text
Odoo -> Provider -> Integration Service -> Snapshot Tables -> /api/integration/* -> Frontend
```

---

## 版本与阶段

## V1：智能客服中台底座

V1 只包含以下三个核心能力：

- 多平台统一客服接入
- 统一订单 / 物流 / 售后上下文
- AI 建议回复 + 人工确认后发送

### V1 不做

以下功能不在 V1 范围内：

- 推荐引擎
- 客户画像
- 营销任务
- 活动运营
- 风控中心
- 质检中心
- ERP 深度集成
- VOC
- 培训中心
- 自动发送
- Deep Agents 主链路
- SaaS 多租户

### V1 当前结论

- V1 已完成并冻结
- 可作为稳定基线版本继续演进

---

## V2：客服运营中台

V2 在 V1 基础上增加“转化和运营”能力，定位从：

> 会答问题

升级为：

> 会接待 + 会推荐 + 会跟单 + 会运营

### V2 已完成的最小运营能力

- Recommendation
- Followup
- Customer Tags
- Customer Profile
- Operation / Campaign
- Analytics
- Risk Flags

### V2 当前后端已完成模块

当前已完成的 V2 backend 7 个最小工程闭环模块：

- Recommendation
- Followup
- Customer Tags
- Customer Profile
- Operation / Campaign
- Analytics
- Risk Flags

这些模块按统一节奏推进，原则上遵循：

```text
design -> model + migration -> repository -> service -> API -> tests -> frontend
```

### V2 当前前端已完成能力

#### Agent Console
当前已完成以下页面与能力：

- 会话详情页增强 Panel
  - FollowupPanel
  - RecommendationPanel
  - RiskFlagPanel
  - CustomerProfilePanel
- 独立页面
  - `/followups`
  - `/operations`
  - `/analytics`

#### Admin Console
当前已完成：

- 首页最小导航入口
- `/operations`
- `/analytics`

### V2 当前前端可验收入口

#### Agent Console
- `/conversations`
- `/conversations/conv_001`
- `/conversations/conv_002`
- `/followups`
- `/operations`
- `/analytics`

#### 会话详情页可验证面板
- FollowupPanel
- RecommendationPanel
- RiskFlagPanel
- CustomerProfilePanel

#### Admin Console
- `/`
- `/operations`
- `/analytics`

### V2 当前前端依赖的主要 API

#### 会话详情相关
- `GET /api/conversations/{id}/recommendations`
- `POST /api/recommendations/{id}/accept`
- `POST /api/recommendations/{id}/reject`
- `GET /api/risk-flags?customer_id=...`
- `POST /api/risk-flags`
- `POST /api/risk-flags/{id}/resolve`
- `POST /api/risk-flags/{id}/dismiss`
- `GET /api/customers/{customer_id}/profile`
- `GET /api/customers/{customer_id}/tags`
- `POST /api/tags`
- `DELETE /api/tags/{id}`

#### 独立页相关
- `/followups` -> `GET /api/follow-up/tasks`
- `/operations` -> `GET /api/operation-campaigns`
- `/analytics` -> `GET /api/analytics/summaries?start_date=&end_date=`

### V2 当前未纳入“已完成”的内容

以下内容当前不应写成“已上线”：

- 完整 dashboard / 图表中心
- 更复杂的后台管理系统
- 权限系统
- 自动推荐引擎
- 个性化排序
- 自动运营编排
- 完整 ERP / OMS / WMS 深度联动
- 完整质检中心
- 完整风控中心
- VOC 分析中心
- 培训中心
- Deep Agents 主链路
- 自动发送回复
- SaaS 多租户

### V2 当前结论

- V2 已完成最小版本并收口
- 不再是当前主开发线

---

## V3：MVP 完整平台阶段

V3 当前结论：

> **V3 MVP 已整体完成**

### 已闭环完成的四个 Phase

#### Phase 1：Quality Inspection Center
- backend：QualityRule / QualityInspectionResult / QualityAlert
- migration / repository / service / API / tests 完成
- Admin Console 最小验证页完成
- 页面状态验证通过

#### Phase 2：Risk Center
- backend：RiskCase / BlacklistCustomer
- 状态流转：resolve / dismiss / escalate
- blacklist add / list / delete
- migration / repository / service / API / tests 完成
- Admin Console 最小验证页完成
- 页面状态验证通过

#### Phase 3：Integration Center
- backend：ERPInventorySnapshot / OrderAuditSnapshot / OrderExceptionSnapshot
- integration API
- explain-status
- migration + seed
- repository / service / API / tests 完成
- Admin Console 最小验证页完成
- inventory / order-audits / order-exceptions 页面正常显示

> 注意：V3 的 Integration Center 完成的是 **mock / seed 驱动的 MVP**，不是真实 ERP/OMS/WMS 接入。

#### Phase 4：Management Analysis / Training Center
- backend：VOCTopic / TrainingCase / TrainingTask / ManagementDashboardSnapshot
- migration + seed
- repository / service / API / tests 完成
- Admin Console 最小验证页完成
- management/voc-topics
- management/training-cases
- management/training-tasks
- management/dashboard-snapshots
- 均已进入 normal

### V3 当前结论

- V3 四个 phase 全部闭环
- V3 MVP 已完成
- 当前不需要继续在 V3 MVP 上无边界扩核心功能

---

## V3.5：Real Odoo Integration Phase

V3.5 不是 V4。  
V3.5 是在 V3 MVP 已完成基础上，进入的：

> **真实业务系统接入强化阶段**

它的目标不是新增新中心，而是把 V3 已完成的 Integration Center 从：

- mock / seed 驱动

升级为：

- 真实 Odoo 驱动

### V3.5 当前一句话定义

> V3.5 是 Omni-CSX 的真实 Odoo 集成阶段。

### V3.5 的系统职责分工

#### Omni-CSX 继续负责
- 多平台消息接入
- 客服中台
- AI 建议回复
- Followup / Recommendation
- Quality / Risk
- explain-status
- 管理分析 / 培训中心
- Agent Console / Admin Console
- 审计、人工确认、统一 API

#### Odoo 负责
- Product / SKU 主数据
- Warehouse / Location
- Inventory facts
- Sales order facts
- 发货 / 履约相关事实
- 后续可扩展的采购、补货、财务等业务事实

### 核心原则
- Odoo 不替代 Omni-CSX
- Odoo 是 ERP / OMS / Inventory / Warehouse 的业务底座
- Omni-CSX 继续做客服 / AI / 运营中台

### V3.5 已完成阶段

#### Phase A：真实只读接入
已完成并收口：

- 真实 Odoo 只读接入
- inventory / order_audit / order_exception 真实链路
- snapshot 写入
- `/api/integration/*` 保持兼容
- explain-status 保持可用

#### Phase B.1：Provider 选择机制 + 最小可观测性
已完成并收口：

- provider_factory
- `ODOO_PROVIDER_MODE`
- sync-status 最小可观测性
- IntegrationSyncStatus 状态记录

#### Phase B.2.1：受控定时刷新
已完成并收口：

- inventory / audit 定时刷新
- startup / shutdown 调度入口
- `manual / scheduled` 触发语义区分

#### Phase B.2.2：snapshot 保留策略 + 手动清理
已完成并收口：

- 最近 N 天保留策略
- 手动清理脚本
- 默认 dry-run
- `--execute`
- `--retention-days`
- `--type`
- 每类最近一条保护
- 排除 IntegrationSyncStatus

#### Phase B.3：order_exception 真实来源升级
已完成并收口：

- `stock.picking` 作为主来源
- 支持 `delay / cancelled`
- 订单关联校验
- `limited_support` 保留
- `sale.order` 仅作兼容 fallback

### V3.5 当前明确未做的内容

以下均属于 **V3.5 明确不做的边界**，不是未完成项：

- 不支持写回
- 不支持双向同步
- 不支持复杂调度平台
- 不支持复杂异常规则引擎
- 不支持前端运维平台
- order_exception 仍不是完整异常系统
- 不支持 `stockout/address/customs`
- 未扩 `mail.activity`
- 未扩 `stock.return.picking`
- 不进入 V4

### V3.5 当前结论

> **V3.5 已全部完成，正式封板。**

---

## 本地开发启动

## 前置要求

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- pnpm workspace

## 启动步骤

### 1. 安装依赖

```bash
# Python 依赖通过 pyproject.toml / requirements 管理
# 前端依赖通过 pnpm workspace 管理
```

### 2. 启动数据库和缓存

```bash
docker compose up -d postgres redis
```

### 3. 启动后端服务

```bash
docker compose up -d api-gateway domain-service ai-orchestrator knowledge-service mock-platform-server
```

### 4. 启动前端服务（可选）

```bash
docker compose up -d agent-console admin-console
```

### 5. 如需重新加载环境变量或镜像变更

```bash
docker compose up -d --force-recreate ai-orchestrator
docker compose up -d --force-recreate agent-console admin-console
```

---

## 验证服务

```bash
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
```

> 实际端口与 compose 配置请以当前仓库中的 docker / compose 文件为准。

---

## 环境变量

关键环境变量通常在 `.env` 文件中配置。

### 基础数据库 / 缓存

```env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=omni_csx
POSTGRES_USER=omni
POSTGRES_PASSWORD=omni

REDIS_HOST=redis
REDIS_PORT=6379

DATABASE_URL=postgresql+psycopg://omni:omni@postgres:5432/omni_csx
```

### AI 相关

```env
OPENAI_API_KEY=your_key_here
OPENAI_BASE_URL=your_base_url_if_needed
OPENAI_MODEL=your_model_name
```

说明：

- 有 `OPENAI_API_KEY` 时，AI Orchestrator 可接真实模型
- 无该变量时，可退回 Mock 模型

### V3.5 / Odoo 相关

请以仓库中的：

- `.ai/v3.5/V3_5_REAL_INTEGRATION_PREP.md`
- `.ai/v3.5/V3_5_REAL_INTEGRATION_RESULT.md`
- `.env.example`

中的实际配置为准。

---

## 服务入口

- API Gateway: `http://localhost:8000`
- Domain Service: `http://localhost:8001`
- AI Orchestrator: `http://localhost:8002`
- Knowledge Service: `http://localhost:8003`
- Mock Platform Server: `http://localhost:8004`
- Agent Console: `http://localhost:3100`
- Admin Console: `http://localhost:3200`

> 如端口有差异，请以实际 compose / 前端配置为准。

---

## 核心 API

## V1 核心 API

| 功能 | API |
|------|-----|
| 会话列表 | `GET /api/conversations` |
| 会话详情 | `GET /api/conversations/{id}` |
| 消息列表 | `GET /api/conversations/{id}/messages` |
| 订单查询 | `GET /api/orders/{platform}/{orderId}` |
| 物流查询 | `GET /api/shipments/{platform}/{orderId}` |
| AI 建议 | `POST /api/ai/suggest-reply` |
| 审计日志 | `GET/POST /api/audit-logs` |
| 文档上传 | `POST /api/kb/documents` |
| 重建索引 | `POST /api/kb/reindex` |

## V2 前端依赖的主要 API

| 功能 | API |
|------|-----|
| Followup 列表 | `GET /api/follow-up/tasks` |
| Followup execute | `POST /api/follow-up/tasks/{id}/execute` |
| Followup close | `POST /api/follow-up/tasks/{id}/close` |
| Recommendation 列表 | `GET /api/conversations/{id}/recommendations` |
| Recommendation accept | `POST /api/recommendations/{id}/accept` |
| Recommendation reject | `POST /api/recommendations/{id}/reject` |
| Risk Flags 列表 | `GET /api/risk-flags?customer_id=...` |
| Risk Flag 创建 | `POST /api/risk-flags` |
| Risk Flag resolve | `POST /api/risk-flags/{id}/resolve` |
| Risk Flag dismiss | `POST /api/risk-flags/{id}/dismiss` |
| Customer Profile | `GET /api/customers/{customer_id}/profile` |
| Customer Tags 列表 | `GET /api/customers/{customer_id}/tags` |
| Tag 创建 | `POST /api/tags` |
| Tag 删除 | `DELETE /api/tags/{id}` |
| Operation 列表 | `GET /api/operation-campaigns` |
| Analytics 摘要 | `GET /api/analytics/summaries?start_date=&end_date=` |

## V3.5 Integration API

| 功能 | API |
|------|-----|
| inventory | `GET /api/integration/inventory` |
| order audits | `GET /api/integration/order-audits` |
| order exceptions | `GET /api/integration/order-exceptions` |
| explain-status | `POST /api/integration/explain-status` |
| sync-status | `GET /api/integration/sync-status` |

---

## 当前前端页面状态要求

当前前端页面和面板按最小闭环要求，应尽量具备以下四态：

- `loading`
- `empty`
- `error`
- `normal`

---

## 当前合理空状态 / 非阻塞项

以下情况在当前阶段属于合理状态，不应一律视为 bug：

- 非电商样本会话展示为空状态
- 某些平台暂不支持物流查询时显示“当前平台暂不支持物流查询”
- `/analytics` 在无历史数据时显示空状态
- Admin Console 当前只有最小导航入口和只读页，不代表缺失完整后台就是 bug

---

## 项目目录结构

```text
.
├── apps/
│   ├── api-gateway/            # 统一 API 入口
│   ├── domain-service/         # 业务主干服务
│   ├── ai-orchestrator/        # AI 工作流编排
│   ├── knowledge-service/      # 知识库服务
│   ├── mock-platform-server/   # 平台 Mock 服务
│   ├── agent-console/          # 客服工作台前端
│   └── admin-console/          # 管理后台前端
├── packages/
│   ├── domain-models/          # 统一领域模型
│   ├── provider-sdk/           # Provider SDK
│   ├── shared-config/          # 共享配置
│   ├── shared-db/              # 共享数据库能力
│   ├── shared-utils/           # 共享工具
│   └── shared-openapi/         # 共享 OpenAPI 产物
├── providers/
│   ├── jd/
│   │   ├── mock/
│   │   └── real/
│   ├── douyin_shop/
│   │   ├── mock/
│   │   └── real/
│   ├── wecom_kf/
│   │   ├── mock/
│   │   └── real/
│   └── odoo/
│       ├── mock/
│       └── real/
├── infra/
│   ├── docker/
│   ├── migrations/
│   └── scripts/
├── migrations/
├── scripts/
├── docs/
├── tests/
└── .ai/
    ├── v1/
    ├── v2/
    ├── v3/
    └── v3.5/
```

---

## 核心服务职责

## apps/api-gateway
统一 API 入口，负责：

- 统一对外路由
- 鉴权 / 中间件
- request_id / 访问日志
- 对前端暴露统一接口

## apps/domain-service
业务主干服务，负责：

- conversations
- messages
- orders
- shipments
- after-sales
- recommendation
- followup
- customer tags
- customer profile
- operation / campaign
- analytics
- risk flags
- integration snapshots
- explain-status

## apps/ai-orchestrator
AI 子系统与工作流，负责：

- intent_chain
- suggest_reply_chain
- tools
- suggest_reply_graph
- 后续 recommendation / followup / campaign 等 AI 工作流扩展

## apps/knowledge-service
知识库服务，负责：

- 文档上传
- 文档切片
- embedding
- retrieval

## apps/mock-platform-server
平台 mock 服务，负责：

- provider mock 接口
- 本地开发与联调支撑
- Mock First 开发流程

## apps/agent-console
客服工作台，负责：

- 会话列表
- 会话详情
- 会话详情 Panel
- `/followups`
- `/operations`
- `/analytics`

## apps/admin-console
管理后台，负责：

- 最小导航入口
- `/operations`
- `/analytics`
- V3/V3.5 阶段的最小验证入口

---

## 工程规则

当前项目已经形成明确工程规则，建议严格遵守：

- 坚持 Mock First
- 坚持 Provider Pattern
- 坚持统一领域模型
- AI 只作为子系统，不承担整个项目主框架
- V1 主链路不允许 AI 自动发送
- AI 输出必须结构化
- 审计日志应记录关键写操作
- 开发顺序固定：

```text
schema / database
-> repository
-> service
-> API
-> OpenAPI
-> tests
-> frontend
```

- 一次只推进一个模块
- 每个模块都尽量形成完整闭环

---

## Git / 分支策略

当前推荐策略如下：

- `main`：稳定主分支
- `v1.0.0`：V1 基线标签
- 其他阶段按独立开发分支推进

建议做法：

- 保持稳定基线干净
- 阶段性功能在独立分支推进
- 不把后续阶段能力反向泄漏到旧基线

---

## 文档体系

### 根目录文档
- `README.md`：仓库总览
- 根目录 `agent.md`：仓库总规则（如存在）

### 阶段文档
- `.ai/v1/`
- `.ai/v2/`
- `.ai/v3/`
- `.ai/v3.5/`

其中，V3.5 的阶段文档用于描述：

- 真实 Odoo 接入边界
- 阶段规划
- 验收清单
- 各子阶段 closeout 文档
- 最终封板说明

---

## 当前项目价值主张

这个项目的核心价值，不是“让 AI 替客服聊天”，而是：

- 统一多平台客服入口
- 统一订单、物流、售后和知识库上下文
- 让 AI 帮客服查信息、组织回复、处理重复问题
- 降低重复劳动
- 提升客服人效
- 统一服务标准
- 增强组织扩展能力
- 为后续更多平台接入和业务自动化提供基础设施

一句话表达：

> 我们做的不是机器人，而是企业的多平台智能客服操作系统。

---

## 当前 README 不应误写为已完成的内容

为了避免 README 与真实进度脱节，当前不建议在首页直接写成“已完成”的内容包括：

- 完整运营工作台
- 完整图表 dashboard
- 完整后台管理体系
- 权限系统
- 自动推荐引擎
- 自动运营编排
- 完整 ERP / OMS / WMS 深度联动
- 完整质检与风控平台
- 更复杂的异常规则引擎
- 写回 / 双向同步能力

这些要么属于更高阶段能力，要么是明确不在当前范围内的边界。

---

## 当前项目最终总结

当前 Omni-CSX 的真实状态可以总结为：

- V1 已完成并冻结
- V2 已完成并收口
- V3 MVP 已完成
- V3.5 已完成并封板

当前仓库的重点不是继续无边界扩功能，而是作为：

> **已完成阶段的稳定基线 + 后续新阶段评审的出发点**

如果后续要继续演进，应重新发起新一轮阶段评审，而不是把新的候选能力继续混入当前已收口范围。