# V2 Acceptance Checklist

## Core positioning
- [x] V2 clearly upgrades V1 from "客服中台底座" to "客服运营中台"
- [x] V2 does not leak into V3 scope

## Recommendation center
- [x] High-intent conversations can generate recommended products (MVP 最小功能)
- [x] Recommendation includes reason and suggested copy
- [ ] Recommendation supports main / substitute / bundle (当前不做扩展类型)
- [x] Human confirmation exists before execution behavior
- [x] Audit logs are recorded (3 events: created, accepted, rejected)

## Follow-up task center
- [x] System identifies consultation-no-order tasks
- [x] System identifies unpaid tasks
- [x] System identifies shipment-exception tasks
- [x] System identifies after-sale follow-up tasks
- [x] Tasks have statuses and suggested copy
- [x] Audit logs are recorded (4 events: created, updated, executed, closed)

## Customer tags and profile
- [x] Customers can receive basic tags
- [ ] Tags include intent / preference / transaction / risk groups (当前仅支持最小 tag_type)
- [x] Profile snapshot can be viewed in console
- [x] Manual correction is supported
- [x] Audit logs are recorded (tags: 2 events, profile: 3 events)

## Customer operation center
- [x] Users can create operation campaigns (MVP)
- [x] Operation campaign has draft/ready/completed/cancelled status
- [x] Operation flow is preview-first and manually confirmed
- [x] No large-scale auto-send is implemented
- [x] Audit logs are recorded (5 events: created, updated, ready, completed, cancelled)

## Analytics
- [x] Analytics summary table exists (MVP)
- [x] Manual summarize API exists (MVP)
- [x] Get summary by date API exists (MVP)
- [x] List summaries by date range API exists (MVP)
- [ ] Dashboard shows conversation volume (当前不做 dashboard 前端)
- [ ] Dashboard shows first response time (当前不做 dashboard 前端)
- [ ] Dashboard shows AI suggestion adoption rate (当前不做 dashboard 前端)
- [x] Audit logs are recorded (1 event: analytics_summary_generated)

## Risk flags (✅ 已完成)
- [x] Risk flag can be created
- [x] Risk flag can be resolved (status: active -> resolved)
- [x] Risk flag can be dismissed (status: active -> dismissed)
- [x] List risk flags by customer_id
- [x] Get risk flag by id
- [x] Audit logs are recorded (3 events: created, resolved, dismissed)
- [x] API semantics: 404 for not found, 400 for invalid status
- [x] Risk flags visible in console (Agent Console 会话详情页 4 态闭环)

## Engineering rules
- [x] All new APIs include OpenAPI annotations
- [x] All new major features include service-level tests
- [x] All new major features include API-level tests
- [x] Provider logic stays separated
- [x] Unified layer is not broken
- [x] All important new actions are audited

## Phase 1 + Phase 2 完成状态

| 模块 | 完成度 |
|------|--------|
| Recommendation MVP | 100% (MVP 最小闭环 + audit) |
| Customer Tags MVP | 100% (MVP 最小闭环 + audit) |
| Customer Profile MVP | 100% (MVP 最小闭环 + audit) |
| Followup MVP | 100% (MVP 最小闭环 + audit) |
| Operation / Campaign MVP | 100% (MVP 最小闭环 + audit) |
| Analytics MVP | 100% (MVP 最小闭环 + audit) |
| Risk Flags MVP | 100% (MVP 最小闭环 + audit) |
| Frontend Agent Console Panel | 100% (4 个 panel: Followup/Recommendation/RiskFlag/CustomerProfile) |
| Frontend Agent Console 独立页 | 100% (/followups + /operations + /analytics) |
| Frontend Admin Console 导航入口 | 100% (首页入口卡片) |
| Frontend Admin Console 只读页 | 100% (/operations + /analytics) |

## 测试状态

- 总计测试数: 319
- 全部通过: ✅

| 模块 | 测试数 |
|------|--------|
| Recommendation | 44 |
| Customer Tags | 27 |
| Customer Profile | 36 |
| Followup | 57 |
| Operation / Campaign | 63 |
| Analytics | 37 |
| Risk Flags | 55 |

## 下一阶段推荐

**推荐：前端整体验收整理**

理由：
1. Backend 7 个 MVP 模块已完成闭环，数据结构已稳定
2. Agent Console 独立页已完成验证
3. Admin Console 已完成首页入口 + 2 只读页
4. V2 Frontend 最小版本已闭环
5. 建议先做整体验收，确保前后端对接无误
6. 不建议直接扩更多页面，应先验收再扩

### Frontend Phase 1 已完成（2026-03-28）
- Agent Console 会话详情页 4 个 panel ✅
- Agent Console 独立页 /followups ✅
- Agent Console 独立页 /operations ✅
- Agent Console 独立页 /analytics ✅
- Admin Console 首页导航入口 ✅
- Admin Console /operations 只读页 ✅
- Admin Console /analytics 只读页 ✅

### 下一阶段
- 前端整体验收整理
