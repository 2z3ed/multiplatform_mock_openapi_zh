# V3.5 真实 Odoo 联调准备说明

本文档用于说明 V3.5 Phase A 第三步的当前状态、阻塞原因、以及拿到真实 Odoo 环境后的恢复方式。

---

## 一、当前状态总结

### 第一步已完成

- OdooMockProvider 已实现并接入
- integration_service 已支持显式注入 odoo_provider
- provider -> service -> snapshot 链路已通过本地测试验证
- /api/integration/* 未受影响
- explain-status 未受影响

### 第二步已完成

- OdooRealProvider 最小骨架已完成
  - `providers/odoo/real/client.py` - XML-RPC 客户端
  - `providers/odoo/real/mapper.py` - 字段映射器
  - `providers/odoo/real/provider.py` - 真实 provider 实现
- `.env.example` 已包含 Odoo 配置模板
- 本地测试已通过（52 个测试全部通过）

### 第三步未完成

**当前状态：待真实 Odoo 环境验证**

### 当前唯一阻塞项

**缺少真实 Odoo 环境配置与真实连接条件**

具体表现：
- 当前仓库没有 `.env` 文件
- 环境变量中没有 `ODOO_*` 相关配置
- 无法验证真实 authenticate / inventory / order_audit / order_exception 链路

---

## 二、真实环境所需配置清单

### 配置项列表

| 配置项 | 用途 | 必填 | 默认值 |
|--------|------|------|--------|
| `ODOO_BASE_URL` | Odoo 实例地址，如 `http://localhost:8069` | 是 | 无 |
| `ODOO_DB` | 数据库名称 | 是 | 无 |
| `ODOO_USERNAME` | 登录用户名 | 是 | 无 |
| `ODOO_API_KEY` | API 密钥（替代密码） | 是 | 无 |
| `ODOO_TIMEOUT` | 请求超时时间（秒） | 否 | `30` |
| `ODOO_VERIFY_SSL` | 是否验证 SSL 证书 | 否 | `true` |

### 配置方式

创建 `.env` 文件（参考 `.env.example`）：

```env
ODOO_BASE_URL=http://your-odoo-host:8069
ODOO_DB=your_database
ODOO_USERNAME=your_username
ODOO_API_KEY=your_api_key
ODOO_TIMEOUT=30
ODOO_VERIFY_SSL=true
```

---

## 三、真实联调前检查清单

在开始联调前，请逐项确认：

### 环境可达性

- [ ] 是否能访问 Odoo 地址（浏览器或 curl 测试）
- [ ] 是否能访问 `/xmlrpc/2/common` 端点
- [ ] 是否能访问 `/xmlrpc/2/object` 端点

### 认证与权限

- [ ] 是否能 authenticate 成功（获取有效 UID）
- [ ] 当前账号是否具备只读权限
- [ ] 当前账号是否能读取 `stock.quant` 模型
- [ ] 当前账号是否能读取 `sale.order` 模型

### 数据可用性

- [ ] 是否存在可读的 `stock.quant` 数据（用于 inventory 链路）
- [ ] 是否存在可读的 `sale.order` 数据（用于 order_audit 链路）
- [ ] 是否存在可用于 exception 推断的数据（如带描述的订单）

### 安全性

- [ ] 当前环境是否为生产环境？
  - 如果是生产环境，**强烈建议使用只读账号**
- [ ] 是否会影响生产数据？
  - 当前实现仅为只读，不会写入 Odoo
- [ ] 是否需要申请专门的联调账号？

---

## 四、联调执行顺序

拿到真实环境后，请按以下顺序验证：

### 1. authenticate 验证

```python
from providers.odoo.real.client import OdooClient

client = OdooClient(
    base_url="http://your-odoo:8069",
    db="your_db",
    username="your_user",
    api_key="your_key",
)
uid = client.authenticate()
print(f"UID: {uid}")
```

预期：返回有效的数字 UID

### 2. stock.quant 验证

```python
quants = client.search_read(
    model="stock.quant",
    domain=[],
    fields=["id", "product_id", "location_id", "quantity", "reserved_quantity"],
    limit=10,
)
print(f"Found {len(quants)} quants")
```

预期：返回库存数据列表

### 3. sale.order 验证

```python
orders = client.search_read(
    model="sale.order",
    domain=[],
    fields=["id", "name", "state", "note"],
    limit=10,
)
print(f"Found {len(orders)} orders")
```

预期：返回订单数据列表

### 4. mapper 输出校验

```python
from providers.odoo.real.mapper import map_inventory, map_order_audit, map_order_exception

# 校验 inventory mapper
for q in quants[:3]:
    print(map_inventory(q))

# 校验 order_audit mapper
for o in orders[:3]:
    print(map_order_audit(o))

# 校验 order_exception mapper
for o in orders[:3]:
    print(map_order_exception(o))
```

预期：输出符合 snapshot 结构的字典

### 5. refresh_from_provider 验证

```python
from providers.odoo.real.provider import OdooRealProvider
from app.services.integration_service import IntegrationService

provider = OdooRealProvider(client)
service = IntegrationService(db_session, odoo_provider=provider)
result = service.refresh_from_provider()
print(result)
```

预期：返回非零的 count 和成功消息

### 6. snapshot 写入验证

```python
inventory_list = service.list_inventory()
audit_list = service.list_order_audits()
exception_list = service.list_order_exceptions()

print(f"Inventory: {len(inventory_list)}")
print(f"Audits: {len(audit_list)}")
print(f"Exceptions: {len(exception_list)}")
```

预期：各列表有数据

### 7. explain-status 验证

```python
# 使用真实数据测试
if inventory_list:
    result = service.explain_status(type="inventory", sku_code=inventory_list[0]["sku_code"])
    print(result)

if audit_list:
    result = service.explain_status(type="audit", order_id=audit_list[0]["order_id"])
    print(result)
```

预期：返回正确的解释和建议

---

## 五、order_exception 风险提示

### 当前实现方式

**order_exception 为有限支持能力**

当前实现：
- 基于 `sale.order.note` 字段的关键词推断
- 检测 "delay" / "stock" / "address" / "customs" 等关键词
- 无匹配时默认 `exception_type = "other"`

### 风险说明

1. **Odoo 无标准 `order_exception` 模型**
   - 这是 Omni-CSX 的统一抽象
   - 不保证 Odoo 里有同名对象

2. **推断依据不稳定**
   - 如果订单没有 note 描述，无法推断异常类型
   - 如果真实环境没有可靠的异常字段，不应宣称该链路已打通

3. **不要为了凑三类全通而编造映射**

### 后续增强方向

如果需要更可靠的 exception 支持，可能需要：
- 基于 `stock.picking` 的发货延迟推断
- 基于 `mail.activity` 的待办事项推断
- 基于自定义字段的异常标记
- 与业务方确认真实的异常判定规则

---

## 六、本地测试运行说明

### 测试命令

```bash
cd /home/zed/multiplatform_mock_openapi_zh

PYTHONPATH=apps/domain-service:packages/shared-config:packages/shared-db:packages/domain-models:packages/provider-sdk:providers python3 -m pytest tests/domain_service/test_integration_service.py tests/domain_service/test_integration_api.py -v
```

### PYTHONPATH 说明

**直接运行 pytest 可能失败**

原因：
- `pytest.ini` 中的 `pythonpath` 配置在某些环境下未被正确解析
- 测试依赖 `shared_db`、`domain_models`、`app` 等模块
- 这些模块位于 `packages/` 和 `apps/` 子目录

解决方案：使用上述完整 PYTHONPATH 命令

### 当前测试通过范围

- 52 个测试全部通过
- 覆盖范围：
  - OdooMockProvider 功能
  - OdooRealProvider 骨架（使用 mock client）
  - integration_service 功能
  - /api/integration/* API
  - explain-status 功能

---

## 七、恢复开发指令

拿到真实 Odoo 环境后，按以下步骤继续第三步联调：

```
1. 创建 .env 文件，填入真实 Odoo 配置
2. 阅读 .ai/v3.5/V3_5_REAL_INTEGRATION_PREP.md
3. 按"联调执行顺序"逐项验证
4. 如发现问题，最小修正 mapper 或 provider
5. 验证 snapshot 写入和 explain-status
6. 输出最终联调结果
7. 不要改 API、不要改前端、不要做写回
```

---

## 八、文档版本

- 创建时间：V3.5 Phase A 第三步暂停时
- 目的：为后续真实联调提供准备材料和操作说明
- 状态：待真实 Odoo 环境验证
