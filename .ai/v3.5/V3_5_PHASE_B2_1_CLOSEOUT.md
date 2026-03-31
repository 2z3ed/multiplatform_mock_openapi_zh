# V3.5 Phase B.2.1 收口文档

## 一、当前阶段结论

### 1.1 完成状态

**Phase B.2.1 已完成**

### 1.2 本轮完成的内容

| 能力 | 说明 |
|------|------|
| 受控定时刷新机制 | 通过配置开关控制定时刷新启用 |
| inventory / audit 定时刷新 | 仅对 inventory 和 order_audit 启用定时刷新 |
| startup/shutdown 调度入口 | main.py 集成调度器生命周期管理 |
| manual / scheduled 触发语义区分 | trigger_type 正确区分手动触发和定时触发 |

### 1.3 本轮未做的内容

| 能力 | 说明 |
|------|------|
| snapshot 清理策略 | 未实现保留策略和清理机制 |
| snapshot 自动清理 | 未实现自动清理功能 |
| order_exception 自动刷新 | order_exception 不进入定时刷新 |
| 前端扩展 | 未新增前端运维页面 |
| 写回能力 | 未实现写回 Odoo 的能力 |

---

## 二、已完成能力清单

### 2.1 配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `ODOO_SCHEDULED_REFRESH_ENABLED` | `false` | 是否启用定时刷新 |
| `ODOO_REFRESH_INTERVAL_INVENTORY` | `900` | inventory 刷新间隔（秒） |
| `ODOO_REFRESH_INTERVAL_AUDIT` | `1800` | audit 刷新间隔（秒） |

### 2.2 调度器模块

| 能力项 | 状态 | 说明 |
|--------|------|------|
| `scheduler/__init__.py` | ✅ 完成 | 导出 start_scheduler, stop_scheduler, is_scheduler_running |
| `scheduler/integration_scheduler.py` | ✅ 完成 | 调度器主逻辑 |
| main.py startup hook | ✅ 完成 | 应用启动时调用 start_scheduler() |
| main.py shutdown hook | ✅ 完成 | 应用关闭时调用 stop_scheduler() |
| 避免重复启动 | ✅ 完成 | `_started` 标志防止重复注册 |

### 2.3 刷新方法

| 方法 | 状态 | 说明 |
|------|------|------|
| `refresh_inventory()` | ✅ 完成 | 独立刷新 inventory |
| `refresh_audit()` | ✅ 完成 | 独立刷新 audit |
| `refresh_from_provider()` | ✅ 保持 | 原有方法行为不变 |

### 2.4 触发语义

| 触发方式 | trigger_type | 说明 |
|----------|--------------|------|
| 手动 refresh_from_provider() | `manual` | 默认值 |
| 定时 refresh_inventory() | `scheduled` | 调度器触发 |
| 定时 refresh_audit() | `scheduled` | 调度器触发 |
| API 触发 | `api` | 可自定义 |

### 2.5 依赖与测试

| 能力项 | 状态 | 说明 |
|--------|------|------|
| APScheduler 依赖接入 | ✅ 完成 | `apscheduler>=3.10.0` |
| 测试通过 | ✅ 完成 | 75/75 测试通过 |
| `/api/integration/*` 未受影响 | ✅ 确认 | 现有 API 功能正常 |
| `explain-status` 未受影响 | ✅ 确认 | 状态解释功能正常 |

---

## 三、边界与限制

### 3.1 定时刷新边界

| 边界项 | 说明 |
|--------|------|
| 只对 inventory / order_audit 启用定时刷新 | order_exception 不进入自动刷新 |
| 默认不开启自动刷新 | `ODOO_SCHEDULED_REFRESH_ENABLED=false` |
| mock 模式不启动 | `ODOO_PROVIDER_MODE=mock` 时调度器不启动 |
| 本地开发环境不应自动启动 | 需显式配置才会启用 |
| 测试环境不应自动启动 | 测试用例显式控制 |

### 3.2 功能限制

| 限制项 | 说明 |
|--------|------|
| 不支持 snapshot 清理 | 未实现清理策略 |
| 不支持自动重试 | 刷新失败不自动重试 |
| 不支持复杂调度平台 | 只使用 APScheduler BackgroundScheduler |
| 不支持前端运维页面 | 只提供 API |
| 不支持写回 | 只读访问 Odoo |

### 3.3 启动条件

```
启动条件：ODOO_PROVIDER_MODE=real 且 ODOO_SCHEDULED_REFRESH_ENABLED=true
不启动条件：mock 模式 / 开关关闭 / 未配置
```

---

## 四、文档与代码产物清单

### 4.1 新增文件

| 文件 | 说明 |
|------|------|
| `apps/domain-service/app/scheduler/__init__.py` | 调度模块初始化 |
| `apps/domain-service/app/scheduler/integration_scheduler.py` | 调度器主文件 |
| `tests/domain_service/test_integration_scheduler.py` | 调度器测试 |
| `.ai/v3.5/V3_5_PHASE_B2_1_CLOSEOUT.md` | 本收口文档 |

### 4.2 修改文件

| 文件 | 说明 |
|------|------|
| `apps/domain-service/app/services/integration_service.py` | 新增 refresh_inventory/refresh_audit 方法 |
| `apps/domain-service/app/main.py` | 添加 startup/shutdown hook |
| `requirements.txt` | 新增 APScheduler 依赖 |
| `.env.example` | 新增定时刷新配置项 |

---

## 五、风险与后续事项

### 5.1 当前风险

| 风险项 | 等级 | 说明 |
|--------|------|------|
| scheduler 多环境边界 | ⚠️ 中 | 已落地，但需继续验证不同运行环境下的启动边界 |
| snapshot 增长 | ⚠️ 中 | 未实现清理策略，可能无限增长 |
| order_exception 有限支持 | ⚠️ 中 | 仍基于关键词推断，不进入自动刷新 |

### 5.2 后续事项

| 事项 | 优先级 | 说明 |
|------|--------|------|
| snapshot 保留策略确认 | P1 | Phase B.2.2 评审确认 |
| snapshot 清理边界确认 | P1 | Phase B.2.2 评审确认 |
| 清理脚本是否进入本阶段 | P1 | Phase B.2.2 评审确认 |
| order_exception 真实来源评估 | P2 | Phase B.3 规划 |
| 前端运维页面 | P3 | 后续规划 |

### 5.3 重要提醒

- 当前只做最小定时刷新，不是完整调度平台
- 不支持分布式调度、任务队列、重试机制
- 生产环境启用前需确认环境配置正确

---

## 六、下一阶段建议

### 6.1 明确建议

| 建议 | 说明 |
|------|------|
| 下一步不应直接进入 Phase B.2.2 编码 | 需先完成评审确认 |
| 下一步应先做 Phase B.2.2 编码前评审确认 | 确认范围后再编码 |

### 6.2 Phase B.2.2 评审主题

| 主题 | 说明 |
|------|------|
| snapshot 保留策略 | 保留 N 天还是 N 条 |
| 清理边界 | 哪些数据需要清理 |
| 清理脚本是否进入本阶段 | 是否在 Phase B.2.2 实现 |
| 自动清理是否继续禁止 | 是否允许自动清理 |

---

## 七、验收确认

| 验收项 | 状态 |
|--------|------|
| 受控定时刷新机制已落地 | ✅ 完成 |
| inventory / audit 定时刷新已落地 | ✅ 完成 |
| manual / scheduled 语义区分正确 | ✅ 完成 |
| 测试通过 | ✅ 完成 (75/75) |
| 现有功能未受影响 | ✅ 确认 |
| 未进入 Phase B.2.2 | ✅ 确认 |
| 未进入 V4 | ✅ 确认 |

---

*收口时间: 2026-03-30*
*Omni-CSX V3.5 Phase B.2.1 Closeout*
