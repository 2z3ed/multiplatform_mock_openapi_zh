# Omni-CSX

Omni-CSX 是一个多平台智能客服运营中台项目。

它的目标不是做一个单点聊天机器人，而是把多平台消息、订单、物流、售后、知识库、AI 建议回复，以及后续运营与管理能力统一到一个中台中。

***

## 当前仓库状态

当前仓库已完成以下阶段：

- **V1**：已完成，作为历史稳定基线保留
- **V2**：最小版本已完成并已收口
- **V3**：MVP 已完成，已形成完整阶段闭环

当前推荐分支：

- `v2-dev`：V2 收口后的稳定开发分支
- `v3-design`：V3 开发与收口分支

当前推荐阶段标签：

- `v2-minimal-closed`
- `v3-mvp-closed`（如已打 tag）

***

## 版本说明

### V1

V1 是“智能客服中台底座”。

V1 只做三件事：

- 多平台统一客服接入
- 统一订单 / 物流 / 售后上下文
- AI 建议回复 + 人工确认后发送

V1 不做推荐、画像、运营任务、质检、风控、ERP 深联、VOC、培训中心等能力。

### V2

V2 是“客服运营中台最小版本”。

V2 在 V1 基础上补齐了最小运营能力，包括：

- Recommendation
- Followup
- Customer Tags
- Customer Profile
- Operation / Campaign
- Analytics
- Risk Flags

V2 最小版本已完成并已收口，可作为稳定阶段节点继续向 V3 演进。

### V3

V3 是“接近商用完整版的平台阶段”。

V3 已完成四个 MVP 模块：

- Phase 1：Quality Inspection Center
- Phase 2：Risk Center
- Phase 3：Integration Center
- Phase 4：Management Analysis / Training Center

当前 V3 已完成 MVP 闭环，可作为交接、演示、收口和下一阶段规划的基线版本。

***

## V3 MVP 已完成功能

### 1. Quality Inspection Center

- 质检规则管理
- 单会话质检执行
- 质检结果查询
- 质检告警查询
- Admin Console 最小验证页

### 2. Risk Center

- 风险事件管理
- 黑名单客户管理
- 风险状态流转
- Admin Console 最小验证页

### 3. Integration Center

- 库存快照查询
- 订单审核状态快照查询
- 异常订单快照查询
- 状态解释输出
- Admin Console 最小验证页

### 4. Management Analysis / Training Center

- VOC 主题沉淀与查询
- 培训案例沉淀与查询
- 训练任务创建与查询
- 管理看板快照生成与查询
- Admin Console 最小验证页

***

## 当前明确未做的内容

当前 V3 仍未进入以下能力：

- 真实 ERP / OMS / WMS 系统对接
- 自动从 conversation 抽取 VOC Topic
- 自动沉淀 Training Case
- occurrence\_count 自动更新逻辑
- 复杂 BI 平台
- 自定义报表系统
- 大屏 / dashboard 可视化平台
- 深度学习训练平台
- 复杂自动优化系统
- Deep Agents 主链路化

这些能力应放在下一阶段规划中，而不是继续无边界扩展当前 V3 MVP。

***

## 仓库中的 AI 协作文件

本仓库将不同版本阶段的 AI 协作上下文独立管理，不直接混在根目录中。

.ai/
v1/
v2/
v3/

当前活跃上下文为：

.ai/v3/

建议按以下顺序读取：

1. `.ai/v3/agent.md`
2. `.ai/v3/README.md`
3. `.ai/v3/V3_ROADMAP.md`
4. `.ai/v3/V3_ACCEPTANCE_CHECKLIST.md`
5. `.ai/v3/prompts/V3_MASTER_PROMPT.txt`
6. `.ai/v3/prompts/V3_TASK_BREAKDOWN.txt`

***

## 根目录文件与版本目录文件的职责

### 根目录 README.md

负责：

- 仓库总览
- 当前项目阶段状态
- V1 / V2 / V3 的版本说明
- 版本上下文入口说明

不负责：

- 详细定义某个阶段的全部规则
- 替代 `.ai/v1/`、`.ai/v2/`、`.ai/v3/` 中的阶段专属文档

### `.ai/v1/`

负责：

- V1 历史基线规则
- V1 专属约束
- V1 相关提示词和文档

### `.ai/v2/`

负责：

- V2 开发和收口阶段规则
- V2 已完成能力的文档基线
- V2 验收与提示词

### `.ai/v3/`

负责：

- V3 正式开发约束
- V3 路线图
- V3 验收清单
- V3 阶段性提示词
- V3 MVP 收口后的阶段说明

***

## 当前开发原则

无论 V1 / V2 / V3，仓库都继续遵守以下原则：

- mock-first
- provider pattern
- 统一领域模型
- human-in-the-loop
- 审计日志必写
- OpenAPI 必须可见
- tests 必须跟上
- 一次只推进一个模块
- backend 先于 frontend
- 不破坏稳定基线

固定开发顺序：

schema/database -> repository -> service -> API -> OpenAPI -> tests -> frontend

***

## 当前建议

当前不要继续在 V3 MVP 上无边界扩功能。

正确做法是：

1. 先完成 V3 MVP 文档收口
2. 完成 Git/tag 阶段节点收口
3. 基于当前 V3 MVP 再进入下一阶段规划
4. 新阶段优先讨论：
   - 真实 ERP 对接
   - 自动抽取 VOC / Training Case
   - 可视化增强
   - 更强的质检 / 风控 / 管理分析能力

***

## 项目目录概览

apps/
packages/
providers/
infra/
docs/
.ai/

如需查看版本专属约束，请进入 `.ai/v1/`、`.ai/v2/`、`.ai/v3/`。
