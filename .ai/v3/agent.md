# Omni-CSX V3 Agent Rules

你现在接手的是 Omni-CSX 项目的 V3 设计与开发阶段。

当前项目状态：

- V1 已完成并已作为稳定基线
- V2 最小版本已完成并已收口
- 当前工作应以 `v2-minimal-closed` 为稳定起点，在 `v3-design` 或后续 V3 分支上推进
- V3 不是重写 V1/V2，而是在既有中台骨架上增加“管理、风控、质检、业务联动、训练优化”能力

\==================================================

1. V3 PRODUCT POSITIONING
   \==================================================

V3 的目标不是“继续补几个客服功能”，而是把系统从“客服运营工具”升级成“接近商用完整版的客服运营平台”。

V3 核心价值：

- 从执行层升级到管理层
- 从客服工作台升级到可管理、可追责、可优化的平台
- 从消息与订单上下文升级到质检、风控、ERP/OMS/WMS 联动、管理分析、训练沉淀

V3 的四大核心模块：

1. 质检中心
2. 风控中心
3. ERP / OMS / WMS 联动中心
4. 管理分析与训练中心

\==================================================
2\. V3 HARD CONSTRAINTS
=======================

必须遵守：

- 继续保持 V1/V2 稳定能力不被破坏
- 继续使用 FastAPI 作为主业务框架
- 继续使用 PostgreSQL + Redis
- 继续使用统一领域模型和 provider pattern
- 继续保持 mock-first
- 继续要求审计日志
- 继续要求 OpenAPI
- 继续要求 tests
- 继续保持 human-in-the-loop，不把高风险动作自动化
- 一次只推进一个模块，不并行开启多个大中心
- 开发顺序必须保持：
  schema/database -> repository -> service -> API -> OpenAPI -> tests -> frontend

禁止：

- 不要重写 V1/V2
- 不要把 V3 做成“全栈重构”
- 不要一次性实现全部四大中心
- 不要为了 V3 改坏现有 unified API
- 不要先做复杂前端大屏，再补后端
- 不要先接全部真实 ERP/provider，再做 mock
- 不要把 Deep Agents 放进客服主链路
- 不要跳过 migration
- 不要跳过 audit
- 不要跳过 tests

\==================================================
3\. V3 TECH STACK RULES
=======================

FastAPI:
必须继续承担：

- REST API
- admin API
- management API
- quality / risk / ERP / training backend
- webhook / trigger endpoints
- OpenAPI generation

LangChain:
用于：

- 结构化抽取
- 解释生成
- 工具调用
- 检索增强
- 质检解释
- 风控解释
- ERP 状态解释话术
- VOC 总结
- 培训案例摘要

LangGraph:
可以在 V3 扩展到以下工作流：

- 质检工作流
- 风控升级工作流
- ERP 异常安抚工作流
- VOC / 训练样本沉淀工作流

Deep Agents:
只允许作为 V3 的旁路复杂分析助手，用于：

- VOC 深度分析
- 培训案例自动生成
- 规则优化建议
  禁止进入：
- 客服接待主链路
- 常规 CRUD/业务 API
- 生产主流程中的关键实时动作

\==================================================
4\. V3 ARCHITECTURE EXPANSION RULE
==================================

V3 允许新增独立 service，但必须有明确职责边界，不允许“服务切分只为了切分”。

优先允许新增的 service：

- quality-inspection-service
- risk-center-service
- integration-service（ERP / OMS / WMS）
- training-or-voc-service（如果确实需要独立）

如果当前阶段只做最小版本，也可以先落在既有 domain-service 内做模块化扩展。
但必须先给出边界说明，再决定是否独立拆 service。

\==================================================
5\. V3 MODULE PRIORITY RULE
===========================

推荐优先级如下：

第一优先级：

1. 质检中心最小闭环
2. 风控中心最小闭环

第二优先级：
3\. ERP / OMS / WMS 联动最小闭环

第三优先级：
4\. 管理分析与训练中心最小闭环

每个模块都要先做“最小闭环”，不要一上来做“大而全平台”。

\==================================================
6\. V3 DATA MODEL RULE
======================

V3 允许新增以下类型的模型：

- QualityRule
- QualityInspectionResult
- QualityAlert
- RiskCase
- BlacklistCustomer
- ERPInventorySnapshot
- OrderAuditSnapshot
- OrderExceptionSnapshot
- VOCTopic
- TrainingCase
- TrainingTask
- ManagementDashboardSnapshot

要求：

- 所有模型必须解释其与 Customer / Conversation / Order / Message / AuditLog 的关系
- 所有原始外部 payload 仍只能落在 raw\_json / extra\_json
- 前端和 AI 层不允许直接消费外部系统原始结构

\==================================================
7\. V3 AUDIT RULE
=================

以下动作必须有 audit：

- 质检规则创建 / 修改 / 启停
- 质检运行
- 高危质检告警派发
- 风险事件创建 / 升级 / 关闭
- 黑名单写入 / 解除
- ERP 异常状态同步
- 训练任务创建 / 完成
- VOC 主题生成
- 管理看板快照生成
- 任何人工 override / 人工复核 / 人工确认动作

没有 audit 的 V3 功能视为未完成。

\==================================================
8\. V3 FRONTEND RULE
====================

V3 前端不是先做华丽大屏，而是先做：

- 可验证的最小管理页
- 可验证的质检结果页
- 可验证的风险事件页
- 可验证的 ERP 状态页
- 可验证的训练任务页

先完成 backend 闭环，再做 frontend。
所有 V3 前端页面初期应以：

- 列表
- 详情
- 状态流转
- 空态 / 错误态 / 正常态
  为主，不优先做复杂可视化。

\==================================================
9\. V3 DEFINITION OF DONE
=========================

V3 某一模块完成，至少要满足：

- model 明确
- migration 明确
- repository 完成
- service 完成
- API 完成
- OpenAPI 可见
- tests 通过
- audit 完整
- 最小 frontend 或最小管理验证入口可用
- 不破坏 V1/V2 现有能力

\==================================================
10\. EXECUTION MODE
===================

每次开始新任务前，必须先输出：

1. 本轮目标
2. 本轮范围
3. 将修改的文件
4. schema / migration 变化
5. API 变化
6. 对 V1/V2 的影响评估
7. tests 范围
8. 本轮明确不做的事

没有新的明确指令，不要继续扩展到下一个模块。
