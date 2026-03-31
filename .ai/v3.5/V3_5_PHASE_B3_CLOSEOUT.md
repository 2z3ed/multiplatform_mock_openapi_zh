# V3.5 Phase B.3 收口文档

## 一、当前阶段结论

### 1.1 阶段状态

**Phase B.3 已完成** ✅

### 1.2 本轮完成的内容

| 功能 | 状态 | 说明 |
|------|------|------|
| stock.picking 主来源接入 | ✅ 已完成 | 从 Odoo stock.picking 获取真实异常数据 |
| delay 映射 | ✅ 已完成 | 基于 scheduled_date vs date_done 判断延误 |
| cancelled 映射 | ✅ 已完成 | 基于 state='cancel' 判断取消 |
| 订单关联校验 | ✅ 已完成 | 验证 origin 对应的 sale.order 存在 |
| limited_support 保留 | ✅ 已完成 | 明确标注有限支持口径 |
| fallback 兼容兜底 | ✅ 已完成 | stock.picking 失败时降级到 sale.order |

### 1.3 本轮未做的内容

| 功能 | 状态 | 说明 |
|------|------|------|
| stockout | ❌ 未做 | 需结合库存数据，本轮不做 |
| address | ❌ 未做 | 无相关字段，本轮不做 |
| customs | ❌ 未做 | 无相关字段，本轮不做 |
| mail.activity 接入 | ❌ 未做 | 本轮只做 stock.picking |
| stock.return.picking 接入 | ❌ 未做 | 本轮只做 stock.picking |
| 前端扩展 | ❌ 未做 | 不改前端 |
| 写回能力 | ❌ 未做 | 保持只读 |

---

## 二、已完成能力清单

### 2.1 Provider 新增方法

| 方法 | 说明 |
|------|------|
| `_get_order_exceptions_from_picking()` | 从 stock.picking 获取异常（内部方法） |

### 2.2 Mapper 新增函数

| 函数 | 说明 |
|------|------|
| `map_order_exception_from_picking()` | 从 stock.picking 映射异常结构 |
| `is_valid_order_origin()` | 验证 origin 是否匹配订单名格式 |
| `parse_datetime()` | 解析各种格式的日期时间 |

### 2.3 delay 判断逻辑

| 条件 | 说明 |
|------|------|
| state = 'done' | 已完成发货 |
| scheduled_date 存在 | 有计划时间 |
| date_done 存在 | 有实际完成时间 |
| date_done > scheduled_date | 存在延误 |

**映射结果**：
- `exception_type`: "delay"
- `exception_status`: "resolved"
- `detected_at`: date_done

### 2.4 cancelled 判断逻辑

| 条件 | 说明 |
|------|------|
| state = 'cancel' | 发货单已取消 |

**映射结果**：
- `exception_type`: "cancelled"
- `exception_status`: "cancelled"
- `detected_at`: create_date

### 2.5 订单关联失败跳过

| 策略 | 说明 |
|------|------|
| 格式初筛 | origin 必须匹配 `^S\d{5,}$` 模式 |
| 真实验证 | 查询 sale.order 确认订单存在 |
| 关联失败 | 直接跳过，不生成异常记录 |
| 禁止伪造 | 不使用 stock.picking.name 作为 order_id |

### 2.6 get_order_exception_list() 保持 list[dict]

**返回类型**：`list[dict[str, Any]]`

不改变对外契约，不返回复合结构。

### 2.7 fallback 条件边界

| 场景 | 处理 |
|------|------|
| stock.picking 读取成功且有异常 | 返回 stock.picking 结果 |
| stock.picking 读取成功但无异常 | 返回空列表（不 fallback） |
| stock.picking 读取失败（异常） | fallback 到 sale.order 关键词推断 |

### 2.8 limited_support 保留

| 要求 | 实现 |
|------|------|
| 不宣称完全打通 | 代码注释标注 "Limited Support" |
| 明确支持类型 | 仅 delay, cancelled |
| 明确数据来源 | stock.picking（主），sale.order（fallback） |
| 说明订单关联不完整 | 注释说明 origin 关联限制 |
| detail_json 标注 | `limited_support: true`, `source: "stock.picking"` |

### 2.9 测试通过情况

**最终验证执行命令**：
```bash
PYTHONPATH="apps/domain-service:apps/mock-platform-server:apps/knowledge-service:packages/shared-config:packages/shared-db:packages/domain-models:packages/provider-sdk:providers" python3 -m pytest tests/domain_service/test_order_exception_mapper.py tests/domain_service/test_integration_service.py tests/domain_service/test_integration_api.py tests/domain_service/test_order_exception_snapshot_repository.py -v --tb=short
```

**各测试文件结果**：

| 测试文件 | 测试数 | 通过 | 失败 | 跳过 | 结果 |
|----------|--------|------|------|------|------|
| test_order_exception_mapper.py | 23 | 23 | 0 | 0 | ✅ 全部通过 |
| test_integration_service.py | 44 | 44 | 0 | 0 | ✅ 全部通过 |
| test_integration_api.py | 20 | 20 | 0 | 0 | ✅ 全部通过 |
| test_order_exception_snapshot_repository.py | 9 | 9 | 0 | 0 | ✅ 全部通过 |
| **总计** | **96** | **96** | **0** | **0** | **✅ 全部通过** |

**测试覆盖范围**：
- `is_valid_order_origin()`: 6 个用例（有效/无效 origin 格式校验）
- `parse_datetime()`: 4 个用例（字符串/对象/None/非法格式解析）
- `map_order_exception_from_picking()`: 8 个用例（delay/cancelled 映射、跳过逻辑）
- Provider `_get_order_exceptions_from_picking()`: 3 个用例（正常/失败/空结果）
- Provider `get_order_exception_list()`: 2 个用例（返回类型/优先级）
- IntegrationService: 22 个用例（CRUD/explain-status/refresh/sync-status）
- OdooRealProvider: 6 个用例（实例化/mock 调用）
- ProviderFactory: 5 个用例（mock/real 切换/错误处理）
- SyncStatusRecording: 5 个用例（状态记录/失败记录/空状态）
- Integration API: 20 个用例（全部端点 + sync-status）
- OrderExceptionSnapshotRepository: 9 个用例（CRUD/cleanup）

**测试总数说明**：与 B.3 收口文档预期 96 个测试一致，无增减。

---

## 三、边界与限制

### 3.1 当前只支持 delay / cancelled

- 不支持 stockout（需结合库存数据）
- 不支持 address（无相关字段）
- 不支持 customs（无相关字段）
- 不支持 other 的复杂推断

### 3.2 当前主来源仅为 stock.picking

- mail.activity 未接入
- stock.return.picking 未接入
- helpdesk/ticket 未接入

### 3.3 sale.order fallback 仅为兼容兜底

- 不代表真实来源已完整打通
- 仅在 stock.picking 读取失败时触发
- 结果标注来源为 sale.order

### 3.4 订单关联不完整

- 只有 origin 匹配 `^S\d{5,}$` 格式时才尝试关联
- 需验证 sale.order 存在才生成异常
- 无法关联的记录直接跳过

### 3.5 不支持复杂异常规则引擎

- 不做规则配置
- 不做自动化决策
- 不做异常闭环处理

### 3.6 不改现有 API 语义

- `/api/integration/*` 不受影响
- explain-status 逻辑不受影响
- 现有测试全部通过

---

## 四、文档与代码产物清单

### 4.1 新增文件

| 文件 | 类型 | 说明 |
|------|------|------|
| `tests/domain_service/test_order_exception_mapper.py` | 测试 | mapper 和 provider 测试 |
| `.ai/v3.5/V3_5_PHASE_B3_CLOSEOUT.md` | 文档 | 本收口文档 |

### 4.2 修改文件

| 文件 | 修改内容 |
|------|----------|
| `providers/odoo/real/provider.py` | 新增 `_get_order_exceptions_from_picking()` 方法，更新 `get_order_exception_list()` |
| `providers/odoo/real/mapper.py` | 新增 `map_order_exception_from_picking()`、`is_valid_order_origin()`、`parse_datetime()` |
| `.ai/v3.5/V3_5_PHASE_B_PLAN.md` | 最小更新：标记 B.3 完成状态 |

### 4.3 未修改文件

- `apps/domain-service/app/services/integration_service.py` - 未修改
- `apps/domain-service/app/api/integration.py` - 未修改
- `providers/odoo/real/client.py` - 未修改
- `providers/odoo/provider_factory.py` - 未修改
- `apps/domain-service/app/scheduler/*` - 未修改
- 前端任何文件 - 未修改
- `.env` - 未修改
- `requirements.txt` - 未修改

---

## 五、风险与后续事项

### 5.1 stock.picking 只能覆盖部分异常语义

| 风险 | 说明 |
|------|------|
| 异常类型有限 | 仅 delay, cancelled |
| 无法发现所有异常 | stockout/address/customs 无法覆盖 |
| 数据依赖 | 依赖 Odoo 数据质量和完整性 |

### 5.2 订单关联仍不完整

| 风险 | 说明 |
|------|------|
| origin 格式限制 | 只有匹配订单名格式的才能关联 |
| 部分记录跳过 | 无法关联的记录不生成异常 |
| 数据丢失风险 | 可能遗漏部分异常 |

### 5.3 mail.activity / stock.return.picking 仍待评估

| 来源 | 状态 | 说明 |
|------|------|------|
| mail.activity | 待评估 | 可作为人工标记异常的补充来源 |
| stock.return.picking | 待评估 | 可作为逆向履约异常来源 |

### 5.4 order_exception 仍保持 limited_support 口径

- 不宣称完全打通
- 不承诺异常完整性
- 不承诺异常准确性
- 不承诺异常实时性

---

## 六、下一阶段建议

### 6.1 下一步不应直接编码

- Phase B.3 已完成收口
- 下一步应先做后续阶段评审确认
- 不跳过评审直接开发

### 6.2 后续阶段评审主题

| 主题 | 说明 |
|------|------|
| mail.activity 是否作为补充来源 | 评估人工标记异常的补充能力 |
| stock.return.picking 是否进入候选 | 评估逆向履约异常来源 |
| stockout / address / customs 是否值得扩展 | 评估扩展异常类型的必要性 |
| 异常统一语义是否需要再收紧 | 评估异常定义和状态的统一性 |

### 6.3 评审产出

- 后续阶段规划文档
- 来源评估报告
- 编码实施确认

---

## 七、文档版本

- 创建时间：V3.5 Phase B.3 完成后
- 目的：记录 Phase B.3 完成状态与边界
- 性质：收口文档

---

*Omni-CSX V3.5 Phase B.3 Closeout*
