# V2 Frontend Phase 1 Status

## 完成时间
2026-03-28

## Agent Console - 会话详情页 Panel

| Panel | 功能 | 状态 |
|-------|------|------|
| FollowupPanel | 查看、执行、关闭 | ✅ 4 态闭环 |
| RecommendationPanel | 查看、接受、拒绝 | ✅ 4 态闭环 |
| RiskFlagPanel | 查看、创建、处理、忽略 | ✅ 4 态闭环 |
| CustomerProfilePanel | 只读展示 | ✅ 4 态闭环 |

## Agent Console - 独立页

| 页面 | 功能 | 状态 |
|------|------|------|
| /followups | 只读列表 + execute / close | ✅ 4 态闭环 |
| /operations | 只读列表 | ✅ 4 态闭环 |
| /analytics | 只读列表（默认最近 7 天） | ✅ 4 态闭环 |

### /analytics API 对齐说明
- Backend: `GET /api/analytics/summaries?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- 前端默认请求最近 7 天
- 不自动调用 POST summarize
- 无数据时显示空状态

## 已完成的前端能力

### 会话详情页内
- Followup：查看、执行、关闭
- Recommendation：查看、接受、拒绝
- Risk Flags：查看、创建、处理、忽略
- Customer Profile / Tags：查看、创建标签、删除标签

### 独立页
- /followups：只读列表 + execute / close
- /operations：只读列表
- /analytics：只读列表

## 依赖的 Backend API

| 页面/Panel | API 路径 |
|------------|----------|
| FollowupPanel | GET `/api/follow-up/tasks`, POST `/api/follow-up/tasks/{id}/execute`, POST `/api/follow-up/tasks/{id}/close` |
| RecommendationPanel | GET `/api/conversations/{id}/recommendations`, POST `/api/recommendations/{id}/accept`, POST `/api/recommendations/{id}/reject` |
| RiskFlagPanel | GET `/api/risk-flags?customer_id=`, POST `/api/risk-flags`, POST `/api/risk-flags/{id}/resolve`, POST `/api/risk-flags/{id}/dismiss` |
| CustomerProfilePanel | GET `/api/customers/{customer_id}/profile`, GET `/api/customers/{customer_id}/tags`, POST `/api/tags`, DELETE `/api/tags/{id}` |
| /followups | GET `/api/follow-up/tasks` (分页) |
| /operations | GET `/api/operation-campaigns` |
| /analytics | GET `/api/analytics/summaries?start_date=&end_date=` |

## Admin Console - 导航入口

| 页面 | 功能 | 状态 |
|------|------|------|
| / | 首页导航入口（5 个卡片链接） | ✅ 已完成 |

### 首页入口包含
- 平台配置
- 知识库管理
- 审计日志
- 运营活动
- 数据概览

## Admin Console - 只读页

| 页面 | 功能 | 状态 |
|------|------|------|
| /operations | 只读列表 | ✅ 4 态闭环 |
| /analytics | 只读列表（默认最近 7 天） | ✅ 4 态闭环 |

### Admin Console 实现特点
- 4 态：loading / empty / error / normal
- 只读展示，不做写操作
- 直接 fetch 模式，未要求 backend 新增接口

### /operations 展示字段
- name, campaign_type, status, target_description, preview_text, created_at

### /analytics 展示字段
- stat_date, recommendation_created_count, recommendation_accepted_count, followup_executed_count, followup_closed_count, operation_campaign_completed_count

## 未完成边界

- 更复杂的 dashboard / 图表
- 更完整的后台管理工作台
- 更多后台管理页
- 权限系统
- 更复杂导航体系

## 下一阶段推荐

**推荐：前端整体验收整理**

理由：
1. Agent Console 已完成：4 panel + 3 独立页
2. Admin Console 已完成：首页入口 + 2 只读页
3. V2 Frontend 最小版本已闭环
4. 建议先做整体验收，确保前后端对接无误
5. 不建议直接扩更多页面，应先验收现有功能

**不推荐当前做：**
- 复杂 dashboard（需要更多业务沉淀）
- 权限系统（V2 暂不涉及）
- 无边界扩页面（应先验收再扩）

## 明确禁止本轮做的事情
- 不要做复杂 dashboard
- 不要继续扩 Agent Console 新页面
- 不要做完整运营工作台
- 不要引入复杂状态管理库
