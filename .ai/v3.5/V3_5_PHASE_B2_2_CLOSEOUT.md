# V3.5 Phase B.2.2 收口文档

## 一、当前阶段结论

### 1.1 阶段状态

**Phase B.2.2 已完成** ✅

### 1.2 本轮完成的内容

| 功能 | 状态 | 说明 |
|------|------|------|
| snapshot 保留策略 | ✅ 已完成 | 默认保留最近 N 天，支持参数覆盖 |
| 手动清理脚本 | ✅ 已完成 | `scripts/cleanup_snapshots.py` |
| 默认 dry-run | ✅ 已完成 | 不传 `--execute` 时只预览 |
| --execute 才删除 | ✅ 已完成 | 显式传入才执行实际删除 |
| --retention-days | ✅ 已完成 | 支持自定义保留天数，默认 7 天 |
| --type 按类型清理 | ✅ 已完成 | 支持 inventory/order_audit/order_exception/all |
| 每类最近一条保护 | ✅ 已完成 | 即使超过保留期也保护最新一条 |
| IntegrationSyncStatus 排除 | ✅ 已完成 | 清理范围明确排除该表 |

### 1.3 本轮未做的内容

| 功能 | 状态 | 说明 |
|------|------|------|
| 自动清理 | ❌ 未做 | 本轮只做手动清理 |
| 定时清理 | ❌ 未做 | 不集成到调度器 |
| order_exception 升级 | ❌ 未做 | 保持有限支持口径 |
| 前端扩展 | ❌ 未做 | 不改前端 |
| 写回能力 | ❌ 未做 | 保持只读 |
| V4 路线 | ❌ 未做 | 不进入 V4 |

---

## 二、已完成能力清单

### 2.1 Repository 新增方法

三个 snapshot repository 均新增 `cleanup_old_snapshots()` 附加方法：

| Repository | 方法 | 说明 |
|------------|------|------|
| ERPInventorySnapshotRepository | `cleanup_old_snapshots()` | 清理库存快照 |
| OrderAuditSnapshotRepository | `cleanup_old_snapshots()` | 清理审核快照 |
| OrderExceptionSnapshotRepository | `cleanup_old_snapshots()` | 清理异常快照 |

**方法签名**：
```python
def cleanup_old_snapshots(
    self,
    retention_days: int = 7,
    dry_run: bool = True,
) -> dict:
    """
    Args:
        retention_days: 保留天数，默认 7 天
        dry_run: 是否只预览，默认 True
        
    Returns:
        dict: {
            "total_count": int,      # 总记录数
            "to_delete_count": int,  # 待删除数
            "protected_count": int,  # 保护数（最新一条）
            "deleted_count": int,    # 实际删除数
        }
    """
```

### 2.2 清理脚本

**文件**: `scripts/cleanup_snapshots.py`

**使用方式**：
```bash
# 预览模式（默认，不删除数据）
python scripts/cleanup_snapshots.py
python scripts/cleanup_snapshots.py --retention-days 14
python scripts/cleanup_snapshots.py --type inventory

# 执行模式（实际删除）
python scripts/cleanup_snapshots.py --execute
python scripts/cleanup_snapshots.py --type all --execute --retention-days 30
```

**参数说明**：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--execute` | False | 执行实际删除，否则只预览 |
| `--retention-days` | 7 | 保留天数 |
| `--type` | all | 清理类型：inventory/order_audit/order_exception/all |

### 2.3 保护规则

- 每类 snapshot 至少保留最近一条
- 即使该记录超过 retention_days，也不删除
- dry-run 和 execute 模式都遵守该规则

### 2.4 IntegrationSyncStatus 排除

- 清理脚本只处理三类 snapshot
- 明确不处理 IntegrationSyncStatus
- 不处理其他业务表、配置表、日志表

### 2.5 测试通过情况

| 测试文件 | 测试数 | 结果 |
|----------|--------|------|
| test_cleanup_snapshots.py | 7 | ✅ 全部通过 |
| test_integration_api.py | 20 | ✅ 全部通过 |
| test_integration_service.py | 30 | ✅ 全部通过 |
| test_integration_scheduler.py | 5 | ✅ 全部通过 |
| test_erp_inventory_snapshot_repository.py | 8 | ✅ 全部通过 |
| test_order_audit_snapshot_repository.py | 8 | ✅ 全部通过 |
| test_order_exception_snapshot_repository.py | 9 | ✅ 全部通过 |
| **总计** | **87** | **✅ 全部通过** |

**运行命令**：
```bash
PYTHONPATH="apps/domain-service:apps/mock-platform-server:apps/knowledge-service:packages/shared-config:packages/shared-db:packages/domain-models:packages/provider-sdk:providers" python3 -m pytest <测试文件> -v
```

---

## 三、边界与限制

### 3.1 当前只做手动清理

- 清理脚本需要手动执行
- 不自动触发清理
- 不集成到调度器

### 3.2 不支持自动清理

- 无后台自动清理任务
- 无基于时间/数量的自动触发

### 3.3 不支持定时清理

- 无定时调度清理
- 需运维手动执行或通过外部调度工具

### 3.4 不处理 snapshot 以外的表

- 只处理 ERPInventorySnapshot
- 只处理 OrderAuditSnapshot
- 只处理 OrderExceptionSnapshot
- 不处理 IntegrationSyncStatus
- 不处理其他业务表

### 3.5 不处理 order_exception 升级

- order_exception 保持有限支持口径
- 不扩展异常来源
- 不升级异常语义

### 3.6 不改现有 API 语义

- 现有 `/api/integration/*` 不受影响
- explain-status 逻辑不受影响
- 现有测试全部通过

---

## 四、文档与代码产物清单

### 4.1 新增文件

| 文件 | 类型 | 说明 |
|------|------|------|
| `scripts/cleanup_snapshots.py` | 脚本 | 手动清理脚本 |
| `tests/domain_service/test_cleanup_snapshots.py` | 测试 | 清理功能测试 |
| `.ai/v3.5/V3_5_PHASE_B2_2_CLOSEOUT.md` | 文档 | 本收口文档 |

### 4.2 修改文件

| 文件 | 修改内容 |
|------|----------|
| `apps/domain-service/app/repositories/erp_inventory_snapshot_repository.py` | 新增 `cleanup_old_snapshots()` 方法 |
| `apps/domain-service/app/repositories/order_audit_snapshot_repository.py` | 新增 `cleanup_old_snapshots()` 方法 |
| `apps/domain-service/app/repositories/order_exception_snapshot_repository.py` | 新增 `cleanup_old_snapshots()` 方法 |
| `.ai/v3.5/V3_5_PHASE_B_PLAN.md` | 最小更新：标记 B.2.2 完成状态 |

### 4.3 未修改文件

- `providers/odoo/*` - 未修改
- `apps/domain-service/app/api/integration.py` - 未修改
- `apps/domain-service/app/scheduler/*` - 未修改
- `apps/domain-service/app/services/integration_service.py` - 未修改
- 前端任何文件 - 未修改
- migration 文件 - 未修改
- `.env.example` - 未修改
- `requirements.txt` - 未修改

---

## 五、风险与后续事项

### 5.1 保留策略当前固定为最近 N 天

- 当前只支持基于天数的保留策略
- 不支持基于数量的保留策略
- 不支持按业务规则定制保留策略

### 5.2 自动清理仍未实现

- 需运维手动执行清理脚本
- 或通过外部调度工具（如 cron）定时执行
- 未来可考虑集成到调度器

### 5.3 是否需要清理 IntegrationSyncStatus 未来再评估

- 当前明确不清理
- 该表记录同步历史，可能有审计价值
- 未来根据数据增长情况再评估

### 5.4 order_exception 仍保持有限支持口径

- 当前异常数据来源仍为关键词推断
- 未接入真实异常数据源
- 需在 Phase B.3 评估真实来源

---

## 六、下一阶段建议

### 6.1 下一步不应直接编码

- Phase B.2.2 已完成收口
- 下一步应先做 Phase B.3 编码前评审确认
- 不跳过评审直接开发

### 6.2 Phase B.3 编码前评审确认主题

| 主题 | 说明 |
|------|------|
| order_exception 真实来源 | 评估 stock.picking / mail.activity 等候选来源 |
| 是否接 stock.picking | 评估发货/配送记录是否可作为异常来源 |
| 异常统一语义 | 确认异常类型、状态的统一定义 |
| API/前端口径克制 | 明确有限支持的外部口径 |

### 6.3 评审产出

- Phase B.3 规划文档
- order_exception 来源评估报告
- 编码实施确认

---

## 七、文档版本

- 创建时间：V3.5 Phase B.2.2 完成后
- 目的：记录 Phase B.2.2 完成状态与边界
- 性质：收口文档

---

*Omni-CSX V3.5 Phase B.2.2 Closeout*
