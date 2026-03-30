
# Omni-CSX V3 Roadmap

## 当前阶段定位

V3 是 Omni-CSX 从“客服运营工具”走向“接近商用完整版平台”的阶段。
当前不是继续扩 V2，而是新增四大管理与联动能力：

1. 质检中心
2. 风控中心
3. ERP / OMS / WMS 联动中心
4. 管理分析与训练中心

---

## Phase 0：V3 设计收敛（必须先做）

目标：
- 明确 V3 范围
- 明确每个中心的最小闭环
- 判断是否独立拆 service
- 明确数据模型、路由、审计、前端入口的最小方案
- 明确不做范围

交付物：
- V3 设计文档
- 第一模块实施计划
- 第一模块文件清单
- 数据模型草案
- 风险点列表

通过标准：
- 不再对 V3 目标和边界反复摇摆
- 能直接进入 Phase 1 编码

---

## Phase 1：质检中心最小闭环

范围：
- quality_rule
- quality_inspection_result
- quality_alert
- 最小规则引擎
- 质检运行接口
- 结果列表 / 详情
- 高危告警
- 质检报表最小聚合
- audit
- tests
- 最小管理页或只读页

当前不做：
- 多模型复杂质检
- 抽样策略平台化
- 高级 BI 看板

通过标准：
- 可对单个会话或一批会话运行质检
- 可看到规则命中结果
- 可对高危结果生成告警
- 关键动作有审计
- API / OpenAPI / tests 完整

---

## Phase 2：风控中心最小闭环

范围：
- risk_case
- blacklist_customer
- 风险检测规则
- 风险升级
- 主管复核状态
- 风险事件查询与处理
- audit
- tests
- 最小管理页

当前不做：
- 复杂模型训练
- 实时流式复杂风控引擎
- 全量自动策略系统

通过标准：
- 可创建 / 识别风险事件
- 可 resolve / dismiss / escalate
- 黑名单可记录
- 风控事件和状态流转可见
- 关键动作有审计

---

## Phase 3：ERP / OMS / WMS 联动最小闭环

范围：
- erp_inventory_snapshot
- order_audit_snapshot
- order_exception_snapshot
- mock ERP / OMS / WMS 接口
- 库存查询
- 审核状态读取
- 异常订单读取
- ERP 状态解释
- 最小管理页 / 列表页
- audit
- tests

当前不做：
- 全部真实 ERP 系统接通
- 复杂多仓多库存优化
- 自动营销联动

通过标准：
- mock ERP 数据可用
- inventory / audit / exception 三类快照可查
- 客服 / 管理后台能查看最小状态
- API / OpenAPI / tests 完整

---

## Phase 4：管理分析与训练中心最小闭环

范围：
- voc_topic
- training_case
- training_task
- management_dashboard_snapshot
- VOC 主题抽取
- 培训案例沉淀
- 训练任务生成
- 管理看板快照
- audit
- tests
- 最小列表与详情页

当前不做：
- 复杂自定义 BI
- 深度学习训练平台
- 自动组织级策略优化系统

通过标准：
- 会话可沉淀为 VOC 主题或 training case
- 训练任务可创建 / 查询
- dashboard snapshot 可生成
- 最小管理页面可验证
- 关键动作有审计

---

## 建议实施顺序

1. 先做质检中心
2. 再做风控中心
3. 再做 ERP / OMS / WMS 联动
4. 最后做管理分析与训练中心

原因：
- 质检和风控最能体现 V3 与 V2 的阶段差异
- ERP 联动依赖 mock-first 与业务上下文，复杂度更高
- 管理分析与训练中心依赖前面三类数据沉淀

---

## 阶段完成判定

V3 不按“大版本一次性交付”推进，而按模块闭环推进。

每一阶段完成都必须满足：
- model
- migration
- repository
- service
- API
- OpenAPI
- tests
- audit
- 最小 frontend 验证页

---

## 当前提醒

- 不要直接从 V3 开始写前端大屏
- 不要一上来独立拆出所有 service
- 不要把 V3 设计成新的“大一统重构”
- 必须以 `v2-minimal-closed` 为稳定基线


