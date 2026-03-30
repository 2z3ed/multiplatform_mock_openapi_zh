# Omni-CSX V3 Acceptance Checklist

## 当前阶段说明

V3 的验收不按“大版本一次性交付”进行，而按模块最小闭环验收。

当前 V3 必须满足：

- 不破坏 V1/V2 既有稳定能力
- 每一阶段只推进一个中心
- 每一阶段都形成 model -> migration -> repository -> service -> API -> OpenAPI -> tests -> frontend 的最小闭环
- 所有高风险动作都必须可审计
- 所有页面都必须有 empty / error / normal 的最小可验证状态

***

## 通用验收门槛（所有 V3 模块都适用）

### Backend

- 数据模型已定义
- migration 已定义
- repository 已完成
- service 已完成
- API 已完成
- OpenAPI 已可见
- tests 已补齐
- audit 已覆盖关键动作

### Frontend

- 至少有一个最小验证入口
- 页面可打开
- empty 状态合理
- error 状态合理
- normal 状态合理
- 不要求复杂 dashboard 先行

### 架构与边界

- 未破坏 V1/V2 稳定能力
- 未越界扩展到其他 V3 模块
- 未将 Deep Agents 引入主链路
- 未跳过 migration / tests / audit

***

## Phase 0：V3 设计收敛验收

- V3 范围明确
- 四大中心优先级明确
- 第一阶段模块已确定
- 第一阶段非目标明确
- 数据模型草案明确
- 服务边界明确
- 目录落位明确
- 风险点明确

通过标准：

- 可直接进入 Phase 1 编码
- 不再反复讨论边界

***

## Phase 1：质检中心最小闭环验收

### Backend

- quality\_rule 模型完成
- quality\_inspection\_result 模型完成
- quality\_alert 模型完成
- 对应 migration 完成
- repository 完成
- service 完成
- API 完成
- OpenAPI 可见
- tests 通过
- audit 完整

### 功能

- 可对单个会话运行质检
- 可按最小批量条件运行质检
- 可查看质检结果列表
- 可查看质检结果详情
- 高危命中可生成告警
- 可看到规则命中证据

### Frontend

- 最小管理页可打开
- 结果列表可见
- 告警列表可见
- empty / error / normal 状态可验证

### 非目标确认

- 未扩展为复杂 BI 看板
- 未引入复杂多模型质检平台
- 未引入大屏优先实现

***

## Phase 2：风控中心最小闭环验收

### Backend

- risk\_case 模型完成
- blacklist\_customer 模型完成
- migration 完成
- repository 完成
- service 完成
- API 完成
- OpenAPI 可见
- tests 通过
- audit 完整

### 功能

- 可创建风险事件
- 可查看风险事件列表
- 可查看风险事件详情
- 可 resolve
- 可 dismiss
- 可 escalate
- 黑名单记录可查询

### Frontend

- 风险事件最小管理页可打开
- 列表可见
- 状态流转可验证
- empty / error / normal 状态可验证

### 非目标确认

- 未扩展为复杂流式风控引擎
- 未引入复杂策略平台
- 未引入组织级大屏

***

## Phase 3：ERP / OMS / WMS 联动最小闭环验收

### Backend

- inventory\_snapshot 模型完成
- order\_audit\_snapshot 模型完成
- order\_exception\_snapshot 模型完成
- migration 完成
- repository 完成
- service 完成
- API 完成
- OpenAPI 可见
- tests 通过
- audit 完整

### 功能

- mock ERP 接口可用
- 可查询库存快照
- 可查询审核状态快照
- 可查询异常订单快照
- 可生成最小 ERP 状态解释

### Frontend

- 最小 ERP 状态页可打开
- 列表 / 详情可见
- empty / error / normal 状态可验证

### 非目标确认

- 未一次性接通所有真实 ERP
- 未扩展为复杂供应链优化系统
- 未自动驱动营销

***

## Phase 4：管理分析与训练中心最小闭环验收

### Backend

- voc\_topic 模型完成
- training\_case 模型完成
- training\_task 模型完成
- management\_dashboard\_snapshot 模型完成
- migration 完成
- repository 完成
- service 完成
- API 完成
- OpenAPI 可见
- tests 通过
- audit 完整

### 功能

- 可从会话沉淀 VOC topic
- 可从会话沉淀 training case
- 可创建 training task
- 可生成 dashboard snapshot
- 可查询最小结果列表和详情

### Frontend

- VOC / training / snapshot 最小入口可打开
- 列表可见
- empty / error / normal 状态可验证

### 非目标确认

- 未扩展为复杂 BI 平台
- 未扩展为训练平台系统
- 未扩展为组织级自动优化引擎

***

## 当前总体通过标准

V3 当前阶段可以视为“通过”，必须同时满足：

- 当前阶段目标模块通过验收
- 文档已同步
- OpenAPI 已同步
- 测试结果可说明
- 审计日志可抽查
- Git 可形成独立阶段节点

