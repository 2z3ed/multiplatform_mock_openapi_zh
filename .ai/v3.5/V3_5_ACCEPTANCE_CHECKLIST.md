# Omni-CSX V3.5 Acceptance Checklist

## 一、阶段目标确认

- 当前阶段已统一命名为 V3.5
- 当前阶段目标已统一为 Odoo Real Integration Phase
- 当前阶段不被误写为 V4
- 当前阶段范围已明确为只读接入，不做深度写回

***

## 二、设计确认

- Odoo 的系统定位已明确为 ERP / OMS / Inventory / Warehouse 业务底座
- Omni-CSX 的系统定位已明确为客服 / AI / 运营中台
- Odoo 不直接替代 Omni-CSX
- Frontend 不直接连接 Odoo
- Snapshot 继续作为中间层
- Provider Pattern 保持不变
- Mock First 保持不变

***

## 三、后端接入验收

### Provider 层

- `providers/odoo/mock` 已建立
- `providers/odoo/real` 已建立
- Odoo provider 支持库存读取
- Odoo provider 支持订单审核/状态读取
- Odoo provider 支持异常/履约异常读取

### Service 层

- `integration_service` 已改为读取 provider
- mock / real provider 可切换
- inventory snapshot 可刷新
- order audit snapshot 可刷新
- order exception snapshot 可刷新

### 数据层

- 继续复用现有 snapshot 表
- snapshot\_at 能正确记录
- source\_json / detail\_json 可保存必要原始结构
- 不向前端直接暴露 Odoo 原始结构

### API 层

- `GET /api/integration/inventory` 可返回真实数据
- `GET /api/integration/order-audits` 可返回真实数据
- `GET /api/integration/order-exceptions` 可返回真实数据
- `POST /api/integration/explain-status` 可继续工作
- OpenAPI 可见
- 错误边界清晰
- Odoo 不可用时系统有可解释降级行为

### 测试

- provider 层测试通过
- service 层测试通过
- API 层测试通过
- explain-status 测试通过
- mock / real 切换测试通过

***

## 四、前端验证验收

- `/integration/inventory` 可访问
- `/integration/order-audits` 可访问
- `/integration/order-exceptions` 可访问
- 页面支持 loading / empty / error / normal
- 当 Odoo 有数据时页面进入 normal
- 当 Odoo 不可用时页面进入可解释错误态或使用最近 snapshot

***

## 五、当前阶段明确不做项验收

- 没有直接把前端改成直连 Odoo
- 没有实现库存写回
- 没有实现订单状态写回
- 没有实现自动出库
- 没有实现复杂双向同步
- 没有实现复杂调度平台
- 没有进入 V4 能力开发

***

## 六、阶段完成标准

当以下条件全部满足时，可判定 V3.5 Phase A 完成：

- [x] Odoo 真实只读接入已完成
- [x] 现有 Integration Center API 保持可用
- [x] explain-status 对真实数据可用
- [x] Admin Console 页面可验证真实数据
- [x] tests 通过
- [x] 文档同步完成
- [x] 可作为下一阶段写回或流程联动的基线版本

***

## 七、V3.5 全阶段完成确认

| 子阶段 | 状态 |
|--------|------|
| Phase A：真实只读接入 | ✅ 已完成 |
| Phase B.1：Provider 选择 + 可观测性 | ✅ 已完成 |
| Phase B.2.1：受控定时刷新 | ✅ 已完成 |
| Phase B.2.2：Snapshot 保留策略 | ✅ 已完成 |
| Phase B.3：order_exception 真实来源升级 | ✅ 已完成（limited_support） |

### order_exception 最终口径

- limited_support 验收通过
- 主来源：stock.picking（delay / cancelled）
- 兼容 fallback：sale.order
- 当前环境无真实异常样本
- 不宣称"全量真实异常链路完成"

### V3.5 封板确认

V3.5 已完成全部既定范围并正式封板。详见 [V3_5_CLOSURE_SUMMARY.md](./V3_5_CLOSURE_SUMMARY.md)。

### V3.5 之外的额外联调问题（独立于 V3.5 主线）

- 消息持久化（agent/customer 消息写入 DB，已通）
- 真实 PlatformSim 回复（端口 9000 未启动）
- conv1 / PlatformSim 实时链路验收

这些是独立联调问题，不是 V3.5 主线未完成项。

