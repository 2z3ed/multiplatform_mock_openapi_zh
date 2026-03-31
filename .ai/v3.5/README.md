# Omni-CSX V3.5

Omni-CSX V3.5 是在 V3 MVP 完成后的真实系统接入强化阶段。

V3 已完成以下四个最小闭环：

- Phase 1：Quality Inspection Center
- Phase 2：Risk Center
- Phase 3：Integration Center
- Phase 4：Management Analysis / Training Center

V3.5 的任务不是新增新的大模块，而是把现有 Integration Center 从 mock / snapshot 驱动升级为真实业务系统驱动。

当前选定的真实业务系统底座为：

- Odoo

***

## 一、V3.5 的一句话目标

在不破坏 Omni-CSX 现有中台结构的前提下，将 Odoo 作为 ERP / OMS / Inventory / Warehouse 业务底座，完成第一阶段真实数据接入。

***

## 二、V3.5 的定位

### Omni-CSX 的定位不变

Omni-CSX 继续作为：

- 客服中台
- AI / 建议回复 / explain-status 中台
- 运营与管理中台
- 质检、风控、培训、分析能力承载层

### Odoo 的定位

Odoo 作为：

- 商品主数据来源
- SKU / 仓库 / 库位 / 库存来源
- 销售订单事实来源
- 发货/履约相关事实来源
- 后续可扩展的业务系统底座

***

## 三、V3.5 当前要解决的问题

当前 V3 Phase 3 已完成 Integration Center MVP，但仍有明显边界：

- 当前 inventory / order-audits / order-exceptions 仍基于 mock 数据或 seed 数据
- 当前 explain-status 仍建立在 mock snapshot 的基础上
- 当前系统尚未进入真实 ERP / OMS / Inventory 接入阶段

V3.5 要解决的核心问题是：

1. 用 Odoo 替换当前 mock integration 数据源
2. 保留现有 snapshot 表和 integration API
3. 保留现有 Admin Console 页面结构
4. 建立真实数据接入能力，而不是推翻现有实现

***

## 四、V3.5 第一阶段范围

当前只做：

### 1. Odoo 只读接入

- 读取库存事实
- 读取订单审核/订单状态事实
- 读取异常/履约异常事实

### 2. 落地到现有 snapshot 表

- ERPInventorySnapshot
- OrderAuditSnapshot
- OrderExceptionSnapshot

### 3. 保持现有 API 可用

继续使用现有：

- `/api/integration/inventory`
- `/api/integration/order-audits`
- `/api/integration/order-exceptions`
- `/api/integration/explain-status`

### 4. 保持现有前端可验证

- `/integration/inventory`
- `/integration/order-audits`
- `/integration/order-exceptions`

***

## 五、V3.5 当前明确不做的内容

当前阶段不要做：

### 业务写回

- 不写回库存
- 不自动改订单
- 不自动出库
- 不自动售后结案
- 不自动退款处理

### 深度系统集成

- 不做复杂双向同步
- 不做复杂 webhook 反向写入
- 不做复杂事件总线
- 不做复杂主数据治理

### 平台级增强

- 不做 BI 平台
- 不做大屏
- 不做 Deep Agents 主链路化
- 不进入 V4

***

## 六、系统设计原则

V3.5 继续坚持以下原则：

- Mock First
- Provider Pattern
- 统一领域模型
- Snapshot 作为中间层
- Frontend 不直连 Odoo
- 现有 V3 API 优先保持兼容
- backend 先于 frontend
- 小模块完整闭环

***

## 七、推荐的实现路线

### Phase A：Odoo Integration Phase 1（当前要做）

目标：

- 通过 Odoo External API 拉取真实业务数据
- 映射成 Omni-CSX 的统一结构
- 落入 snapshot 表
- API 和前端页面继续工作

### Phase B：有限写回（后续）

目标：

- 只写回低风险动作
- 例如订单备注、客服备注、少量状态补充

### Phase C：流程联动（更后续）

目标：

- Followup / Recommendation / Risk / Quality 与 Odoo 订单/库存事实联动

***

## 八、目录与文档结构

当前 V3.5 文件放置在：

.ai/v3\_5/

包括：

- `agent.md`
- `README.md`
- `V3_5_ROADMAP.md`
- `V3_5_ACCEPTANCE_CHECKLIST.md`
- `prompts/V3_5_MASTER_PROMPT.txt`
- `prompts/V3_5_BACKEND_PROMPT.txt`

***

## 九、当前结论

V3.5 不是新产品阶段，而是 V3 的真实业务接入强化阶段。

当前正确动作不是推翻 V3，而是：

1. 保持 Omni-CSX 作为客服 / AI / 运营中台
2. 让 Odoo 成为业务事实底座
3. 用 Provider + Snapshot 的方式完成只读真实接入
4. 在现有结构上完成增强与收口

