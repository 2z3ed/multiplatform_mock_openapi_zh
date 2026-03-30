V3 Phase 2（Risk Center MVP）已完成最小闭环：

- backend：
  - RiskCase / BlacklistCustomer model / migration / repository / service / API / audit / tests 已完成
  - 当前测试结果：53 passed
- frontend：
  - Admin Console 已完成 /risk/cases 与 /risk/blacklist 最小验证页
  - 同源 API route 已完成
  - 当前已通过 normal 态验证（使用最小演示数据）

说明：
本轮前端验证基于本地 dev 模式完成；如需与既有容器方式完全一致，可在后续统一回 docker 运行方式。
