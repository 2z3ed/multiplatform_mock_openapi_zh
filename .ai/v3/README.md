# Omni-CSX V3

Omni-CSX V3 是在 V1 稳定基线与 V2 最小版本收口基础上，进入“接近商用完整版平台”的阶段。

当前 V3 不再处于“设计中”或“部分实现中”状态。\
当前 V3 已完成 MVP 闭环，并已形成完整的四阶段交付结果。

***

## 一、V3 当前状态

V3 当前状态：

- **Phase 1：Quality Inspection Center** —— 已完成
- **Phase 2：Risk Center** —— 已完成
- **Phase 3：Integration Center** —— 已完成
- **Phase 4：Management Analysis / Training Center** —— 已完成

当前 V3 已达到：

- backend 最小闭环完成
- Admin Console 最小验证入口完成
- 各阶段页面状态验证完成
- 可作为阶段收口节点
- 可作为后续版本规划基线

***

## 二、V3 的目标（已达成的 MVP 范围）

V3 的目标不是继续补若干客服功能，而是把系统从“客服运营工具”升级成“可管理、可追责、可优化、可联动”的平台。

V3 MVP 已完成以下 4 个核心模块：

### 1. Quality Inspection Center

已完成能力：

- 质检规则管理
- 单会话质检执行
- 质检结果查询
- 质检告警查询
- Admin Console 最小验证页

### 2. Risk Center

已完成能力：

- 风险事件管理
- 黑名单客户管理
- 风险状态流转
- Admin Console 最小验证页

### 3. Integration Center

已完成能力：

- 库存快照写入与查询
- 订单审核状态快照写入与查询
- 异常订单快照写入与查询
- 状态解释输出
- Admin Console 最小验证页

### 4. Management Analysis / Training Center

已完成能力：

- VOC 主题沉淀与查询
- 培训案例沉淀与查询
- 训练任务创建与查询
- 管理看板快照生成与查询
- Admin Console 最小验证页

***

## 三、V3 MVP 的工程原则

V3 MVP 继续遵守以下工程原则：

- mock-first
- provider pattern
- 统一领域模型
- human-in-the-loop
- audit 必写
- OpenAPI 必须可见
- tests 必须跟上
- 一模块一闭环
- backend 先于 frontend
- 不破坏既有 stable baseline

固定开发顺序：

schema/database -> repository -> service -> API -> OpenAPI -> tests -> frontend

***

## 四、V3 已完成的阶段结构

### Phase 1：Quality Inspection Center

已完成：

- QualityRule
- QualityInspectionResult
- QualityAlert
- 质检执行接口
- 规则查询接口
- 结果查询接口
- 告警查询接口
- Admin Console 最小验证入口

### Phase 2：Risk Center

已完成：

- RiskCase
- BlacklistCustomer
- 风险事件查询
- 风险状态流转
- 黑名单管理
- Admin Console 最小验证入口

### Phase 3：Integration Center

已完成：

- ERPInventorySnapshot
- OrderAuditSnapshot
- OrderExceptionSnapshot
- 快照写入接口
- 快照读取接口
- explain-status 接口
- Admin Console 最小验证入口

### Phase 4：Management Analysis / Training Center

已完成：

- VOCTopic
- TrainingCase
- TrainingTask
- ManagementDashboardSnapshot
- 创建接口
- 列表接口
- Admin Console 最小验证入口

***

## 五、V3 当前明确未做内容

尽管 V3 MVP 已完成，但以下内容仍未纳入当前版本：

### 质检 / 风控增强

- 批量质检
- 规则启停增强
- 自动风险识别
- 风险规则引擎
- 流式风控

### Integration 增强

- 真实 ERP / OMS / WMS 对接
- 自动刷新 / 定时同步
- 写回 ERP
- 复杂 explain-status 话术增强

### Management / Training 增强

- 按 ID 详情查询 API
- occurrence\_count 自动更新逻辑
- 从 conversation 自动抽取 VOC Topic
- 从 conversation 自动沉淀 Training Case
- 复杂训练流程引擎

### 可视化增强

- dashboard 大屏
- 图表系统
- 自定义 BI 平台
- 复杂筛选、分页、排序、过滤

### 平台级增强

- Deep Agents 主链路化
- 深度学习训练平台
- 自动优化系统

***

## 六、V3 当前推荐定位

当前 V3 推荐定位为：

**V3 MVP Completed**

这意味着：

- 可以作为交接节点
- 可以作为演示节点
- 可以作为后续版本规划基线
- 不建议继续在当前版本上无边界叠加功能

***

## 七、V3 后续建议方向

如果后续继续推进，建议方向如下：

### 1. 真实业务联动增强

- 接真实 ERP / OMS / WMS
- 接真实审核与异常状态来源

### 2. 自动沉淀增强

- 从 conversation 自动抽取 VOC
- 从 conversation 自动沉淀 Training Case
- occurrence\_count 自动更新

### 3. 可视化增强

- 管理看板增强
- 图表与 dashboard
- 更丰富的多维度统计

### 4. 智能增强

- 更复杂的质检与风控规则
- explain-status 增强
- 更强的训练与优化能力

***

## 八、V3 文档结构

当前 V3 相关文件包括：

.ai/v3/
agent.md
README.md
V3\_ROADMAP.md
V3\_ACCEPTANCE\_CHECKLIST.md
prompts/
V3\_MASTER\_PROMPT.txt
V3\_TASK\_BREAKDOWN.txt
V3\_BACKEND\_PROMPT.txt
V3\_FRONTEND\_PROMPT.txt
V3\_DATA\_AND\_RULES\_PROMPT.txt
V3\_PHASE0\_PROMPT.txt

***

## 九、V3 当前建议

当前不要继续把 V3 当成“持续开发中的无限阶段”。

正确做法是：

1. 将当前 V3 定义为 MVP 完成态
2. 完成 README / checklist / roadmap 同步
3. 完成 Git / tag 收口
4. 再基于 V3 MVP 规划下一阶段

一句话结论：

**Omni-CSX V3 MVP 已完成。当前应先收口，再规划下一阶段。**
