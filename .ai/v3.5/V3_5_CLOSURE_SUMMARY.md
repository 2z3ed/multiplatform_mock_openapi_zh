# Omni-CSX V3.5 封板总结

## 一、V3.5 已完成并封板

V3.5（Real Odoo Integration Phase）已全部完成既定范围，正式封板。

本阶段在 V3 MVP 已完成的 Integration Center（mock/snapshot 驱动）基础上，成功升级为真实 Odoo 数据驱动，形成可用于后续业务联动的基础设施。

---

## 二、各子阶段完成状态

| 子阶段 | 状态 | 说明 |
|--------|------|------|
| Phase A：真实只读接入 | ✅ 已完成 | inventory / order_audit / order_exception 真实链路 |
| Phase B.1：Provider 选择 + 可观测性 | ✅ 已完成 | provider_factory / ODOO_PROVIDER_MODE / sync-status |
| Phase B.2.1：受控定时刷新 | ✅ 已完成 | inventory / audit 定时刷新 / startup-scheduled 触发 |
| Phase B.2.2：Snapshot 保留策略 | ✅ 已完成 | 最近 N 天保留 / 手动清理 / dry-run / --execute |
| Phase B.3：order_exception 真实来源升级 | ✅ 已完成 | stock.picking 主来源 / limited_support 保留 |

---

## 三、各模块最终结论

### inventory

**真实链路完成。**

- Odoo stock.quant → Odoo provider → integration service → ERPInventorySnapshot → `/api/integration/inventory`
- 定时刷新已配置
- 保留策略已配置

### order_audit

**真实链路完成。**

- Odoo sale.order → Odoo provider → integration service → OrderAuditSnapshot → `/api/integration/order-audits`
- 定时刷新已配置

### order_exception

**limited_support 验收通过。**

- 主来源：Odoo stock.picking（支持 delay / cancelled）
- 兼容 fallback：sale.order
- 当前明确限制：
  - 当前环境无真实异常样本
  - 不宣称"全量真实异常链路完成"
  - limited_support 保留

---

## 四、未进入 V4

V3.5 封板后，未进入 V4 阶段。后续如需继续演进，应重新发起新一轮阶段评审。

---

## 五、V3.5 之外的额外联调问题

以下内容 **不属于 V3.5 主线**，而是独立联调问题：

### 1. 消息持久化

- Agent 发送消息可写入 message 表
- Customer 最小入站消息可写入 message 表
- 刷新/重进后消息仍存在
- 这是 V3.5 之外的额外联调成果，不是 V3.5 主线的一部分

### 2. 真实 PlatformSim 回复

- PlatformSim 服务（端口 9000）当前未启动
- `_get_user_reply_with_retry` 连接被拒绝
- 客户自动回复链路不通
- 这是独立的 PlatformSim 联调问题，不是 V3.5 未完成项

### 3. conv1 / PlatformSim 实时链路验收

- 旧 mock 会话（conv1~conv7）与 PlatformSim 的实时链路尚未在真实环境下完成全量验收
- 这是独立的联调验证问题，不是 V3.5 主线的一部分

---

## 六、封板说明

V3.5 已完成全部既定范围并正式封板。

当前仓库的重点不是继续在 V3.5 范围内无边界扩功能，而是作为：

> **已完成阶段的稳定基线 + 后续新阶段评审的出发点**
