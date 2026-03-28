# V2 Backend Phase 1 阶段状态

## 阶段一句话总结

V2 backend Phase 1 + Phase 2 已完成 7 个核心 MVP 模块（Recommendation、Customer Tags、Customer Profile、Followup、Operation / Campaign、Analytics、Risk Flags）的最小功能闭环 + audit logging，全部 304 个测试通过。

## 完成时间

2026-03-28

## 已完成模块列表

### 1. Recommendation MVP

| 完成项 | 状态 |
|--------|------|
| model | ✅ packages/domain-models/domain_models/models/recommendation.py |
| migration | ✅ infra/migrations/0015_create_recommendation.sql |
| repository | ✅ apps/domain-service/app/repositories/recommendation_repository.py |
| service | ✅ apps/domain-service/app/services/recommendation_service.py |
| API | ✅ apps/domain-service/app/api/recommendation.py |
| tests | ✅ 44 tests |
| audit | ✅ 3 events |

**Audit Events:**
- recommendation_created
- recommendation_accepted
- recommendation_rejected

### 2. Customer Tags MVP

| 完成项 | 状态 |
|--------|------|
| model | ✅ packages/domain-models/domain_models/models/customer_tag.py |
| migration | ✅ infra/migrations/0013_create_customer_tag.sql |
| repository | ✅ apps/domain-service/app/repositories/customer_tag_repository.py |
| service | ✅ apps/domain-service/app/services/tag_service.py |
| API | ✅ apps/domain-service/app/api/tags.py |
| tests | ✅ 27 tests |
| audit | ✅ 2 events |

**Audit Events:**
- customer_tag_created
- customer_tag_deleted

### 3. Customer Profile MVP

| 完成项 | 状态 |
|--------|------|
| model | ✅ packages/domain-models/domain_models/models/customer_profile.py |
| migration | ✅ infra/migrations/0014_create_customer_profile.sql |
| repository | ✅ apps/domain-service/app/repositories/customer_profile_repository.py |
| service | ✅ apps/domain-service/app/services/profile_service.py |
| API | ✅ apps/domain-service/app/api/profile.py |
| tests | ✅ 36 tests |
| audit | ✅ 3 events |

**Audit Events:**
- customer_profile_created
- customer_profile_updated
- customer_profile_deleted

### 4. Followup MVP

| 完成项 | 状态 |
|--------|------|
| model | ✅ packages/domain-models/domain_models/models/follow_up_task.py |
| migration | ✅ infra/migrations/0012_create_follow_up_task.sql |
| repository | ✅ apps/domain-service/app/repositories/followup_task_repository.py |
| service | ✅ apps/domain-service/app/services/followup_service.py |
| API | ✅ apps/domain-service/app/api/followup.py |
| tests | ✅ 57 tests |
| audit | ✅ 4 events |

**Audit Events:**
- followup_task_created
- followup_task_updated
- followup_task_executed
- followup_task_closed

### 5. Operation / Campaign MVP

| 完成项 | 状态 |
|--------|------|
| model | ✅ packages/domain-models/domain_models/models/operation_campaign.py |
| migration | ✅ infra/migrations/0016_create_operation_campaign.sql |
| repository | ✅ apps/domain-service/app/repositories/operation_campaign_repository.py |
| service | ✅ apps/domain-service/app/services/operation_campaign_service.py |
| API | ✅ apps/domain-service/app/api/operation_campaign.py |
| tests | ✅ 63 tests |
| audit | ✅ 5 events |

**Audit Events:**
- operation_campaign_created
- operation_campaign_updated
- operation_campaign_ready
- operation_campaign_completed
- operation_campaign_cancelled

### 6. Analytics MVP

| 完成项 | 状态 |
|--------|------|
| model | ✅ packages/domain-models/domain_models/models/analytics_summary.py |
| migration | ✅ infra/migrations/0017_create_analytics_summary.sql |
| repository | ✅ apps/domain-service/app/repositories/analytics_summary_repository.py |
| service | ✅ apps/domain-service/app/services/analytics_service.py |
| API | ✅ apps/domain-service/app/api/analytics.py |
| tests | ✅ 37 tests |
| audit | ✅ 1 event |

**Audit Events:**
- analytics_summary_generated

**指标口径：**
- recommendation_created_count: 按 created_at 统计
- recommendation_accepted_count: 按 status=accepted + updated_at 统计
- followup_executed_count: 按 status=completed + completed_at 统计
- followup_closed_count: 按 status=closed + completed_at 统计
- operation_campaign_completed_count: 按 status=completed + updated_at 统计

### 7. Risk Flags MVP (Step 1-4 完成)

| 完成项 | 状态 |
|--------|------|
| model | ✅ packages/domain-models/domain_models/models/risk_flag.py |
| migration | ✅ infra/migrations/0018_create_risk_flag.sql |
| repository | ✅ apps/domain-service/app/repositories/risk_flag_repository.py |
| service | ✅ apps/domain-service/app/services/risk_flag_service.py |
| API | ✅ apps/domain-service/app/api/risk_flag.py |
| tests | ✅ 55 tests |
| audit | ✅ 3 events |

**Audit Events:**
- risk_flag_created
- risk_flag_resolved
- risk_flag_dismissed

**API 语义修正：**
- resolve/dismiss 记录不存在 -> 404
- resolve/dismiss 记录存在但状态不合法 -> 400

## 当前测试通过情况

| 测试套件 | 通过数 |
|----------|--------|
| Recommendation tests | 44 |
| Customer Tags tests | 27 |
| Customer Profile tests | 36 |
| Followup tests | 57 |
| Operation / Campaign tests | 63 |
| Analytics tests | 37 |
| Risk Flags tests | 55 |
| **总计** | **319** |

## 当前明确未完成的模块

- Frontend (Agent Console / Admin Console)
- 复杂 dashboard
- 复杂 analytics
- 自动规则引擎
- 完整风险中心
- VOC / 质检中心

## 当前明确不做的范围

- 推荐引擎/算法
- 自动推荐触发
- 自动发送推荐消息
- 个性化排序
- recommendation_type 扩展
- 自动画像聚合
- 自动打标
- 自动跟单规则引擎
- VOC 分析
- 质量检查中心
- 风险中心（完整）
- ERP/OMS/WMS 深度集成
- 训练中心
- 完整商业交付系统

## 下一阶段推荐

### 推荐顺序：Frontend 最小版本

理由：
1. Backend 7 个 MVP 模块已完成闭环，数据结构已稳定
2. V1 Agent Console 已有基础 UI，可以逐步叠加新 panel
3. Frontend 开发可以验证后端 API 正确性
4. 避免 backend 继续扩模块导致与 Frontend 脱节

### Frontend 最小版本应包含：
- Recommendation panel (只读/只操作)
- Follow-up task panel (只读/只操作)
- Customer profile side panel (只读/只操作)
- Risk flags badge (只读)
- Analytics summary (只读)
- Operation campaign list (只读/只操作)

### 不推荐继续扩 backend 大模块的原因：
- 7 个模块已完成最小闭环
- 继续增加 backend 模块会导致与 Frontend 开发脱节
- 当前代码库已足够复杂，需要先验证端到端体验

## 进入下一阶段前的注意事项

1. 当前 Phase 1 + Phase 2 已覆盖 7 个核心 MVP + audit logging
2. 后续模块开发必须保持与当前风格一致
3. 继续保持"小模块完整闭环"开发方式
4. 所有新模块必须包含最小 audit logging
5. 不要破坏 V1 已有的 unified 层和 provider 层

## 阶段验收结论

**V2 backend Phase 1 + Phase 2 视为阶段完成。**

---

## V2 Frontend 最小版本状态

### 已完成模块

| Panel | 位置 | 完成功能 |
|-------|------|----------|
| FollowupPanel | Agent Console /conversations/[id] | 列表、执行、关闭 |
| RecommendationPanel | Agent Console /conversations/[id] | 列表、接受、拒绝 |
| RiskFlagPanel | Agent Console /conversations/[id] | 列表、创建、处理、忽略 |
| CustomerProfilePanel | Agent Console /conversations/[id] | 画像展示、标签列表、创建、删除 |

### 对接 API

- Followup: `/api/follow-up/tasks`
- Recommendation: `/api/conversations/{id}/recommendations`
- Risk Flags: `/api/risk-flags`
- Customer Profile: `/api/customers/{id}/profile`
- Customer Tags: `/api/customers/{id}/tags`

### 未完成模块

- 独立列表页 (/followups, /operations, /analytics)
- Admin Console 扩展
- 复杂 dashboard
- 完整运营工作台

### 下一阶段推荐

**推荐：Admin Console 最小扩展**

理由：
1. Agent Console 已闭环客服主路径
2. Admin Console 有现成框架可复用
3. 运营管理是 V2 完整能力的必要补充
