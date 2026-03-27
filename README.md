# Omni-CSX V1

Omni-CSX V1 多平台统一客服系统。

## V1 范围

V1 仅包含以下三个功能：
- 多平台统一客服接入
- 统一订单/物流/售后上下文
- AI 建议回复 + 人工确认后发送

## 本地开发启动

### 前置要求
- Python 3.11+
- Node.js 20+
- Docker & Docker Compose

### 启动步骤

1. **安装依赖**
```bash
# Python 依赖已通过 pyproject.toml 管理
# 前端依赖通过 pnpm 管理（项目使用 pnpm workspace）
```

2. **启动数据库和缓存**
```bash
docker compose up -d postgres redis
```

3. **启动后端服务**
```bash
docker compose up -d api-gateway domain-service ai-orchestrator knowledge-service mock-platform-server
```

4. **启动前端服务**（可选）
```bash
docker compose up -d agent-console admin-console
```

### 验证服务

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

## 环境变量

关键环境变量在 `.env` 文件中配置：

```
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=omni_csx
POSTGRES_USER=omni
POSTGRES_PASSWORD=omni

REDIS_HOST=redis
REDIS_PORT=6379

DATABASE_URL=postgresql+psycopg://omni:omni@postgres:5432/omni_csx
```

## API 入口

- API Gateway: http://localhost:8000
- Domain Service: http://localhost:8001
- AI Orchestrator: http://localhost:8002
- Knowledge Service: http://localhost:8003
- Mock Platform: http://localhost:8004

### 核心 API

| 功能 | API |
|------|-----|
| 会话列表 | GET /api/conversations |
| 会话详情 | GET /api/conversations/{id} |
| 消息列表 | GET /api/conversations/{id}/messages |
| 订单查询 | GET /api/orders/{platform}/{orderId} |
| 物流查询 | GET /api/shipments/{platform}/{orderId} |
| AI 建议 | POST /api/ai/suggest-reply |
| 审计日志 | GET/POST /api/audit-logs |
| 文档上传 | POST /api/kb/documents |
| 重建索引 | POST /api/kb/reindex |

## V1 已完成功能

### 后端
- [x] API Gateway 统一入口
- [x] Domain Service 业务逻辑
- [x] AI Orchestrator LangGraph 工作流
- [x] Knowledge Service 文档管理
- [x] Mock Platform Server 模拟平台
- [x] 审计日志持久化 (PostgreSQL)
- [x] 所有必需 Provider Mock 实现

### 前端
- [x] Agent Console 登录页
- [x] Agent Console 会话列表
- [x] Agent Console 会话详情（7 个面板）
- [x] Admin Console 平台配置
- [x] Admin Console 知识库管理
- [x] Admin Console 审计日志

### 测试
- [x] Service 层测试通过
- [x] API 层测试通过
- [x] 集成测试覆盖主链路

## V2/V3 延后功能

以下功能不在 V1 范围内：
- 推荐引擎 (Recommendation Engine)
- 客户画像 (Customer Profile)
- 营销任务 (Marketing Tasks)
- 质量检查中心 (Quality Inspection)
- 风险中心 (Risk Center)
- ERP 深度集成 (ERP Deep Integration)
- VOC 分析
- 培训中心的
- Deep Agents
- 自动回复发送
- SaaS 多租户

## 目录结构

```
.
├── apps/
│   ├── api-gateway/       # 统一 API 入口
│   ├── domain-service/    # 业务逻辑服务
│   ├── ai-orchestrator/  # AI 工作流编排
│   ├── knowledge-service/# 知识库服务
│   ├── mock-platform-server/# 模拟平台
│   ├── agent-console/     # 客服工作台前端
│   └── admin-console/     # 管理后台前端
├── packages/
│   ├── domain-models/     # 领域模型
│   ├── provider-sdk/      # Provider SDK
│   ├── shared-config/     # 共享配置
│   ├── shared-db/         # 共享数据库
│   └── shared-utils/      # 共享工具
├── providers/
│   ├── jd/               # 京东 Provider
│   ├── douyin_shop/      # 抖音商城 Provider
│   └── wecom_kf/         # 企业微信客服 Provider
├── infra/
│   ├── docker/           # Docker 配置
│   └── migrations/        # 数据库迁移
└── tests/                # 测试
```