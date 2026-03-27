# Omni-CSX V2 文件包

这是一套为 **V2：客服运营中台** 准备的执行文件包，用于喂给 OpenCode / Codex / Cursor / Claude Code。

## 文件说明

- `agent.md`：V2 总体代理说明，定义目标、边界、开发顺序、架构约束。
- `V2_MASTER_PROMPT.txt`：总控提示词，适合每次开工前先喂一次。
- `V2_TASK_BREAKDOWN.txt`：V2 按模块拆解的任务清单。
- `V2_BACKEND_PROMPT.txt`：后端实现专用提示词。
- `V2_FRONTEND_PROMPT.txt`：前端实现专用提示词。
- `V2_DATA_AND_RULES_PROMPT.txt`：标签、推荐、跟单、风险、分析规则专用提示词。
- `V2_ACCEPTANCE_CHECKLIST.md`：V2 验收标准与完成定义。
- `V2_ROADMAP.md`：V2 模块优先级与里程碑。

## 建议使用方式

1. 先把 `agent.md` 和 `V2_MASTER_PROMPT.txt` 一起给工具读取。
2. 再按具体工作流，选择对应模块提示词：
   - 后端：`V2_BACKEND_PROMPT.txt`
   - 前端：`V2_FRONTEND_PROMPT.txt`
   - 数据与规则：`V2_DATA_AND_RULES_PROMPT.txt`
3. 每做完一块，对照 `V2_ACCEPTANCE_CHECKLIST.md` 自检。
4. 所有开发都必须建立在 V1 冻结基线上，不得破坏 unified 层和 provider 层约束。

## 关键原则

- V2 不是继续修 V1，而是把系统从“统一客服工作台”升级为“客服运营中台”。
- V2 新增模块：商品推荐、智能跟单、客户标签与画像、客户运营、基础运营分析、轻量风险提醒。
- 仍然坚持 mock-first、provider pattern、structured AI output、audit logging、人工确认优先。
