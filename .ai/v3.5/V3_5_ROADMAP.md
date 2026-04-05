# Omni-CSX V3.5 Roadmap

## 阶段定义

V3.5 = Real Odoo Integration Phase

目标不是新增新中心，而是在 V3 已完成 Integration Center MVP 的基础上，接入真实 Odoo 数据源，形成可用于下一阶段业务联动的基础设施。

***

## 当前总体目标

1. 引入 Odoo provider
2. 建立 Odoo mock / real 双实现
3. 保持现有 integration service 不推翻
4. 保持现有 snapshot 表继续作为统一中间层
5. 保持现有 `/api/integration/*` 接口兼容
6. 保持 explain-status 可继续使用
7. 保持现有前端页面可验证

***

## Phase A：Odoo Integration Phase 1（当前主目标）

### 目标

把当前 mock / seed 驱动的 Integration Center 升级为 Odoo 实时读取驱动。

### 范围

- providers/odoo/mock
- providers/odoo/real
- provider-sdk 中的 Odoo 接口抽象
- integration\_service 对接 Odoo provider
- inventory snapshot 刷新
- order audit snapshot 刷新
- order exception snapshot 刷新
- 现有 integration API 兼容
- tests
- Admin Console 验证

### 交付物

- Odoo provider 层代码
- integration service 改造
- snapshot 刷新逻辑
- `/api/integration/*` 真实数据可读
- explain-status 对真实 snapshot 可用
- `/integration/*` 页面可显示真实数据

### 不做

- 不写回 Odoo
- 不改订单状态
- 不改库存
- 不做双向同步
- 不做调度平台
- 不做前端结构重构

***

## Phase B：有限写回（后续）

### 目标

在只读稳定后，补少量低风险写回能力。

### 范围

- 订单备注回写
- 客服处理备注回写
- 异常处理补充信息回写

### 不做

- 不做财务写回
- 不做库存写回
- 不做自动出库
- 不做自动售后结案

***

## Phase C：流程联动（后续）

### 目标

让 Odoo 事实数据与 Omni-CSX 的 Followup / Recommendation / Risk / Quality 形成联动。

### 可能范围

- Recommendation 参考库存可售状态
- explain-status 基于真实订单履约状态增强
- Risk / Quality 参考订单履约或异常事实
- Dashboard 读取更真实的业务指标

***

## 当前优先级

### P0

- 明确 Odoo 接入边界
- 确认 provider 设计
- 确认 Phase A 的只读闭环方案

### P1

- 编码实现 Odoo real provider
- 改造 integration service
- 完成 snapshot 写入与读取
- 完成 API 和 tests

### P2

- 完成 Admin Console 页面验证
- 完成 V3.5 文档同步
- 做阶段收口

***

## 当前版本边界总结

### 已完成（V3）

- Quality Center
- Risk Center
- Integration Center MVP（mock/snapshot）
- Management / Training Center

### 已完成并封板（V3.5）

- Odoo 真实只读接入（Phase A）
- Provider 选择机制 + 最小可观测性（Phase B.1）
- 受控定时刷新（Phase B.2.1）
- Snapshot 保留策略 + 手动清理（Phase B.2.2）
- order_exception 真实来源升级（Phase B.3，limited_support）

详见：[V3_5_CLOSURE_SUMMARY.md](./V3_5_CLOSURE_SUMMARY.md)

### 暂不进入

- V4
- 复杂 BI
- 复杂自动化
- Deep Agents 主链路化

### V3.5 之外的额外联调问题（独立于 V3.5 主线）

- 消息持久化（agent/customer 消息写入 DB，已通）
- 真实 PlatformSim 回复（端口 9000 未启动，自动回复链路不通）
- conv1 / PlatformSim 实时链路验收

这些是独立联调问题，不是 V3.5 主线未完成项。

