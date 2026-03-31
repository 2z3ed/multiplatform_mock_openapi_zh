# Omni-CSX V3.5 Agent

这是 Omni-CSX 的 V3.5 阶段专用协作文件。

V3.5 不是一个全新版本，也不是 V4。\
V3.5 是在 V3 MVP 已完成的基础上，进入“真实业务系统接入强化阶段”的工程阶段。

当前 V3 已完成以下四个闭环模块：

- Phase 1：Quality Inspection Center
- Phase 2：Risk Center
- Phase 3：Integration Center
- Phase 4：Management Analysis / Training Center

V3.5 的核心目标不是继续扩新的中心，而是把 V3 已有的 Integration Center 从 mock/snapshot 驱动，升级为真实 ERP/OMS 数据接入能力。

***

## 一、当前阶段一句话定义

V3.5 是 Omni-CSX 的真实 Odoo 集成阶段。

当前目标是：

- 保持 Omni-CSX 作为客服 / AI / 运营中台
- 让 Odoo 成为 ERP / OMS / Inventory / Warehouse 的业务底座
- 通过 Provider Pattern 将 Odoo 接入到现有 Integration Center
- 保持现有 snapshot 表、现有 integration API、现有 explain-status 能力
- 不推翻 V3 既有结构

***

## 二、当前活跃目标

当前唯一优先目标：

实现 Odoo Integration Phase 1（只读集成）。

第一阶段只做：

1. 从 Odoo 读取真实库存数据
2. 从 Odoo 读取真实订单审核/订单状态数据
3. 从 Odoo 读取真实异常/履约异常数据
4. 将真实数据落入现有 snapshot 表
5. 保持 `/api/integration/*` 和 `explain-status` 继续可用
6. 在不改前端结构的前提下完成真实数据切换

***

## 三、V3.5 的硬边界

### 当前必须做的

- 保持现有 V3 Integration Center 结构
- 新增 Odoo provider
- 保持 Provider Pattern
- 保持 snapshot 作为中间层
- 保持统一 API
- 保持 explain-status
- 完整走 backend 工程闭环：
  model / migration（如需要） -> provider -> service -> API -> tests -> frontend 验证

### 当前明确不做的

- 不进入 V4
- 不新增新的大中心
- 不重写 Omni-CSX 的前后台
- 不让前端直接访问 Odoo
- 不直接把 Odoo 原始字段透传给前端
- 不做真实 ERP 写回
- 不做库存扣减
- 不做自动出库
- 不做退款、财务、采购等深度写操作
- 不做复杂双向同步
- 不做定时调度系统平台化
- 不做复杂 BI
- 不做大屏
- 不做 Deep Agents 主链路化

***

## 四、系统职责分工

### Omni-CSX 继续负责

- 多平台消息接入
- 会话中台
- AI 建议回复
- Followup / Recommendation
- Quality / Risk
- explain-status
- 管理分析 / 培训沉淀
- Agent Console / Admin Console
- 审计、人工确认、统一 API

### Odoo 负责

- Product / SKU 主数据
- Warehouse / Location
- Inventory facts
- Sales order facts
- 履约/发货相关事实
- 后续可扩展的采购、补货、财务等业务事实

***

## 五、工程总原则

V3.5 继续沿用全项目既有原则：

- Mock First
- Provider Pattern
- 统一领域模型
- Human-in-the-loop
- 审计必写
- OpenAPI 必须可见
- tests 必须跟上
- 一次只推进一个模块
- backend 先于 frontend
- 不破坏稳定基线

固定推进顺序：

schema/database -> provider -> service -> API -> OpenAPI -> tests -> frontend

***

## 六、当前推荐实现策略

当前推荐策略是：

Odoo -> Odoo Provider -> Integration Service -> Snapshot Tables -> Omni-CSX API -> Frontend

而不是：

Odoo -> Frontend

或者：

Odoo -> 前端直连 -> 页面展示

这样做的原因：

1. 保持统一领域模型
2. 保持缓存和降级能力
3. 保持审计能力
4. Odoo 不可用时仍可使用最近一次 snapshot
5. 后续若替换 ERP，不需要重写前端

***

## 七、当前版本命名

当前阶段统一命名为：

V3.5：Real Odoo Integration Phase

不要把这一步叫成 V4。\
这是 V3 的增强阶段，不是新产品阶段。

***

## 八、开始前必须优先读取

1. `.ai/v3_5/agent.md`
2. `.ai/v3_5/README.md`
3. `.ai/v3_5/V3_5_ROADMAP.md`
4. `.ai/v3_5/V3_5_ACCEPTANCE_CHECKLIST.md`
5. `.ai/v3_5/prompts/V3_5_MASTER_PROMPT.txt`
6. `.ai/v3_5/prompts/V3_5_BACKEND_PROMPT.txt`

***

## 九、默认工作方式

如果没有额外说明，当前任务默认按以下方式理解：

1. 当前任务属于 V3.5
2. 先读取 `.ai/v3_5/` 文件
3. 优先只做 Odoo Integration Phase 1
4. 先 backend，后 frontend
5. 优先保持最小改动，不推翻现有 V3 结构
6. 当前所有结论都要服务于“从 mock 走向真实接入”这个目标

