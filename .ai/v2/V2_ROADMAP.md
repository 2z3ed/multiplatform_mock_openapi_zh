# V2 Roadmap

## Phase 1: Domain and data foundation (✅ 已完成)
- [x] migrations
- [x] ORM models
- [x] audit events
- [x] repository layer

### Phase 1 完成模块
- [x] Recommendation MVP (model + migration + repository + service + API + tests + audit)
- [x] Customer Tags MVP (model + migration + repository + service + API + tests + audit)
- [x] Customer Profile MVP (model + migration + repository + service + API + tests + audit)
- [x] Followup MVP (model + migration + repository + service + API + tests + audit)

## Phase 2: Operation and Analytics (✅ 已完成)
- [x] Operation / Campaign MVP (model + migration + repository + service + API + tests + audit)
- [x] Analytics MVP (model + migration + repository + service + API + tests + audit)

## Phase 3: Risk Flags (✅ 已完成)
- [x] risk_flag model
- [x] risk_flag repository
- [x] risk_flag service
- [x] risk_flag API
- [x] audit logging
- [x] API semantics: 404 for not found, 400 for invalid status

## Phase 4: Frontend Integration (✅ 已完成)
- [x] Agent Console 会话详情页 4 个 panel (Followup/Recommendation/RiskFlag/CustomerProfile)
- [x] Agent Console 独立页 /followups
- [x] Agent Console 独立页 /operations
- [x] Agent Console 独立页 /analytics
- [x] Admin Console 首页导航入口
- [x] Admin Console /operations 只读页
- [x] Admin Console /analytics 只读页

## Delivery priority
1. ~~recommendation center~~ ✅ Phase 1 完成
2. ~~follow-up task center~~ ✅ Phase 1 完成
3. ~~customer tags and profile snapshot~~ ✅ Phase 1 完成
4. ~~operation task center~~ ✅ Phase 2 完成
5. ~~analytics~~ ✅ Phase 2 完成
6. ~~risk flags~~ ✅ Phase 3 完成 (55 tests passed)
7. ~~frontend integration~~ ✅ 已完成

## Explicit non-goals for V2
- full quality inspection center
- full risk center
- ERP / OMS / WMS deep integration center
- VOC analysis center
- training center
- full commercial delivery system
- automatic recommendation engine
- automatic tagging
- automatic follow-up rules
- complex analytics dashboard
- complex operation automation
