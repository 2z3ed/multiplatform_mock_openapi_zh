# V3.5 真实 Odoo 联调结果报告

## 一、部署方式

### 1.1 Odoo Docker 部署

使用 Docker Compose 部署 Odoo 18 + PostgreSQL 17：

```yaml
# odoo-deployment/docker-compose.yml
version: '3.8'
services:
  db:
    image: postgres:17
    container_name: odoo-db
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data
    restart: always

  odoo:
    image: odoo:18
    container_name: odoo-app
    depends_on:
      - db
    ports:
      - "8069:8069"
      - "20018:8072"
    volumes:
      - odoo-data:/var/lib/odoo
      - ./addons:/mnt/extra-addons
      - ./etc:/etc/odoo
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    restart: always

volumes:
  odoo-db-data:
  odoo-data:
```

启动命令：
```bash
cd odoo-deployment
docker-compose up -d
```

### 1.2 Odoo 模块安装

登录 Odoo 后台 (http://localhost:8069)，安装以下模块：
- **Inventory** (库存管理) - 提供 `stock.quant` 模型
- **Sales** (销售管理) - 提供 `sale.order` 模型
- **Products** 默认已安装

---

## 二、Odoo 配置方法

### 2.1 环境变量配置

创建 `.env` 文件：

```env
ODOO_BASE_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=your-email@example.com
ODOO_API_KEY=your-api-key-here
ODOO_TIMEOUT=30
ODOO_VERIFY_SSL=false
```

### 2.2 API Key 生成

1. 登录 Odoo 后台
2. 进入 Settings > Users & Companies > Users
3. 选择用户，点击 "API Keys"
4. 生成新的 API Key

### 2.3 Odoo 配置文件

```ini
# odoo-deployment/etc/odoo.conf
[options]
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
data_dir = /var/lib/odoo
admin_passwd = admin
http_port = 8069
longpolling_port = 8072
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
```

---

## 三、联调结果

### 3.1 refresh_from_provider 验证

| 项目 | 结果 | 数量 |
|------|------|------|
| inventory_count | ✅ 成功 | 38 条 |
| audit_count | ✅ 成功 | 40 条 |
| exception_count | ✅ 成功 | 40 条 |

### 3.2 Snapshot 写入验证

| Snapshot 类型 | 状态 | 写入数量 |
|---------------|------|----------|
| ERPInventorySnapshot | ✅ 成功 | 38 条 |
| OrderAuditSnapshot | ✅ 成功 | 40 条 |
| OrderExceptionSnapshot | ✅ 成功 | 40 条 |

### 3.3 API 验证

| API 端点 | 状态 | 说明 |
|----------|------|------|
| list_inventory | ✅ 正常 | 可读取真实 snapshot |
| list_order_audits | ✅ 正常 | 可读取真实 snapshot |
| list_order_exceptions | ✅ 正常 | 可读取真实 snapshot |

### 3.4 explain-status 验证

| 类型 | 状态 | 示例输出 |
|------|------|----------|
| inventory | ✅ 正常 | "商品 XXX 当前缺货，暂无法发货。" |
| audit | ✅ 正常 | "订单 XXX 正在审核中，请耐心等待。" |
| exception | ✅ 正常 | "订单 XXX 存在异常：其他异常，当前状态：open。" |

---

## 四、有限支持项

### 4.1 order_exception 有限支持

**状态**: ⚠️ 有限支持 (Limited Support)

**原因**:
- `exception_type` 基于关键词推断，非真实异常数据
- 当前实现从 `sale.order` 模型读取，通过 `note` 字段关键词推断异常类型
- Odoo 中没有独立的"订单异常"模块

**推断逻辑**:
```python
def map_order_exception(order: dict) -> dict:
    note = order.get("note", "") or ""
    note_lower = note.lower()
    
    if "delay" in note_lower:
        exception_type = "delay"
    elif "stock" in note_lower or "out of stock" in note_lower:
        exception_type = "stockout"
    elif "address" in note_lower:
        exception_type = "address"
    elif "customs" in note_lower:
        exception_type = "customs"
    else:
        exception_type = "other"
```

**后续建议**:
- 对接 Odoo 的真实异常/退货模块（如 `stock.return.picking` 或自定义模块）
- 或使用 Odoo 的 `crm.lead` 或 `helpdesk.ticket` 作为异常来源

---

## 五、文件清单

### 5.1 新增文件

| 文件 | 说明 |
|------|------|
| `.env` | Odoo 连接配置 |
| `odoo-deployment/docker-compose.yml` | Docker 部署配置 |
| `odoo-deployment/etc/odoo.conf` | Odoo 配置文件 |
| `test_odoo_connection.py` | Odoo 连接测试脚本 |
| `test_v35_full_integration.py` | 完整联调测试脚本 |
| `check_odoo_models.py` | Odoo 模型检查脚本 |

### 5.2 已有文件（V3.5 新增/修改）

| 文件 | 说明 |
|------|------|
| `providers/odoo/real/client.py` | Odoo XML-RPC 客户端 |
| `providers/odoo/real/provider.py` | OdooRealProvider 实现 |
| `providers/odoo/real/mapper.py` | 数据映射函数 |
| `providers/odoo/mock/provider.py` | OdooMockProvider 实现 |
| `apps/domain-service/app/services/integration_service.py` | 集成服务（支持 provider 注入） |

---

## 六、验证命令

### 6.1 运行完整联调测试

```bash
cd /home/zed/multiplatform_mock_openapi_zh
python3 test_v35_full_integration.py
```

### 6.2 运行 pytest 测试

```bash
PYTHONPATH=apps/domain-service:packages/shared-config:packages/shared-db:packages/domain-models:packages/provider-sdk:providers python3 -m pytest tests/domain_service/test_integration_service.py tests/domain_service/test_integration_api.py -v --tb=short
```

---

## 七、结论

### 7.1 V3.5 第三步完成状态

| 验证项 | 状态 |
|--------|------|
| refresh_from_provider 成功消费真实 provider | ✅ 完成 |
| 三类 snapshot 写入成功 | ✅ 完成 |
| /api/integration/* 基于真实 snapshot 正常工作 | ✅ 完成 |
| explain-status 正常 | ✅ 完成 |
| order_exception 有限支持说明 | ✅ 已说明 |

### 7.2 当前第三步判定

**✅ V3.5 Phase A 第三步已完成**

唯一注意事项：
- `order_exception` 为有限支持，基于关键词推断
- 后续需要对接真实异常数据源

---

*报告生成时间: 2026-03-30*
*Omni-CSX V3.5 Real Odoo Integration*
