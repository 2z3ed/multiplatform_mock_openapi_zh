# Omni-CSX Agent Bootstrap

这是仓库根目录的引导文件，不是某个版本的完整规则文件。

## 当前活跃开发阶段

当前活跃版本：V3\
当前活跃分支：`v3-design`

## 开始前必须先读

1. `.ai/v3/agent.md`
2. `.ai/v3/README.md`
3. `.ai/v3/V3_ROADMAP.md`
4. `.ai/v3/V3_ACCEPTANCE_CHECKLIST.md`

如果是具体任务，再继续读：

- backend：`.ai/v3/prompts/V3_BACKEND_PROMPT.txt`
- frontend：`.ai/v3/prompts/V3_FRONTEND_PROMPT.txt`
- 设计收敛：`.ai/v3/prompts/V3_PHASE0_PROMPT.txt`
- 模型/规则设计：`.ai/v3/prompts/V3_DATA_AND_RULES_PROMPT.txt`

## 历史版本上下文

- `.ai/v1/`：V1 历史基线
- `.ai/v2/`：V2 开发与收口
- `.ai/v3/`：当前正式开发约束

不要把 V1 / V2 的局部规则直接套到 V3。

## 全局要求

- 不重写 V1 / V2
- 不破坏稳定基线
- 一次只推进一个模块
- backend 先于 frontend
- 必须保留 migration / audit / tests / OpenAPI

