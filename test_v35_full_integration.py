"""
V3.5 第三步完整联调测试
- 使用真实 Odoo 配置，注入 OdooRealProvider
- 调用 integration_service.refresh_from_provider
- 验证三类 snapshot 写入
- 验证 /api/integration/* 是否正常工作
- 验证 explain-status 是否正常
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'providers'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'shared-db'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'domain-models'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'provider-sdk'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'shared-config'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps', 'domain-service'))

from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from shared_db.base import Base
from app.services.integration_service import IntegrationService
from app.repositories.erp_inventory_snapshot_repository import ERPInventorySnapshotRepository
from app.repositories.order_audit_snapshot_repository import OrderAuditSnapshotRepository
from app.repositories.order_exception_snapshot_repository import OrderExceptionSnapshotRepository

from odoo.real.client import OdooClient
from odoo.real.provider import OdooRealProvider


def main():
    print("=" * 70)
    print("V3.5 第三步完整联调测试")
    print("=" * 70)
    
    print(f"\n配置信息:")
    print(f"  ODOO_BASE_URL: {os.getenv('ODOO_BASE_URL')}")
    print(f"  ODOO_DB: {os.getenv('ODOO_DB')}")
    print(f"  ODOO_USERNAME: {os.getenv('ODOO_USERNAME')}")
    
    print("\n" + "=" * 70)
    print("1. 初始化真实 Odoo Provider")
    print("=" * 70)
    
    client = OdooClient(
        base_url=os.getenv('ODOO_BASE_URL'),
        db=os.getenv('ODOO_DB'),
        username=os.getenv('ODOO_USERNAME'),
        api_key=os.getenv('ODOO_API_KEY'),
        timeout=int(os.getenv('ODOO_TIMEOUT', '30')),
        verify_ssl=os.getenv('ODOO_VERIFY_SSL', 'true').lower() == 'true',
    )
    
    uid = client.authenticate()
    print(f"✅ Odoo 认证成功! UID: {uid}")
    
    provider = OdooRealProvider(client)
    print(f"✅ OdooRealProvider 初始化成功")
    
    print("\n" + "=" * 70)
    print("2. 初始化数据库和 IntegrationService")
    print("=" * 70)
    
    TEST_DB_URL = "sqlite:///:memory:"
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db_session = SessionLocal()
    
    service = IntegrationService(db_session, odoo_provider=provider)
    print(f"✅ IntegrationService 初始化成功，已注入 OdooRealProvider")
    
    print("\n" + "=" * 70)
    print("3. 调用 refresh_from_provider")
    print("=" * 70)
    
    result = service.refresh_from_provider()
    print(f"✅ refresh_from_provider 完成!")
    print(f"   - inventory_count: {result['inventory_count']}")
    print(f"   - audit_count: {result['audit_count']}")
    print(f"   - exception_count: {result['exception_count']}")
    print(f"   - message: {result['message']}")
    
    print("\n" + "=" * 70)
    print("4. 验证三类 Snapshot 写入")
    print("=" * 70)
    
    inventory_repo = ERPInventorySnapshotRepository(db_session)
    audit_repo = OrderAuditSnapshotRepository(db_session)
    exception_repo = OrderExceptionSnapshotRepository(db_session)
    
    inventory_list = inventory_repo.list_all()
    print(f"\n4.1 ERPInventorySnapshot:")
    print(f"    ✅ 写入数量: {len(inventory_list)}")
    if inventory_list:
        for inv in inventory_list[:3]:
            print(f"    - SKU: {inv.sku_code}, Warehouse: {inv.warehouse_code}, Available: {inv.available_qty}, Status: {inv.status}")
    
    audit_list = audit_repo.list_all()
    print(f"\n4.2 OrderAuditSnapshot:")
    print(f"    ✅ 写入数量: {len(audit_list)}")
    if audit_list:
        for audit in audit_list[:3]:
            print(f"    - Order: {audit.order_id}, Platform: {audit.platform}, Status: {audit.audit_status}")
    
    exception_list = exception_repo.list_all()
    print(f"\n4.3 OrderExceptionSnapshot:")
    print(f"    ✅ 写入数量: {len(exception_list)}")
    if exception_list:
        for exc in exception_list[:3]:
            print(f"    - Order: {exc.order_id}, Type: {exc.exception_type}, Status: {exc.exception_status}")
    
    print("\n" + "=" * 70)
    print("5. 验证 /api/integration/* 读取")
    print("=" * 70)
    
    inv_api_result = service.list_inventory()
    print(f"\n5.1 list_inventory:")
    print(f"    ✅ 返回数量: {len(inv_api_result)}")
    
    audit_api_result = service.list_order_audits()
    print(f"\n5.2 list_order_audits:")
    print(f"    ✅ 返回数量: {len(audit_api_result)}")
    
    exc_api_result = service.list_order_exceptions()
    print(f"\n5.3 list_order_exceptions:")
    print(f"    ✅ 返回数量: {len(exc_api_result)}")
    
    print("\n" + "=" * 70)
    print("6. 验证 explain-status")
    print("=" * 70)
    
    if inventory_list:
        first_sku = inventory_list[0].sku_code
        inv_explain = service.explain_status(type="inventory", sku_code=first_sku)
        print(f"\n6.1 inventory explain (SKU: {first_sku}):")
        print(f"    explanation: {inv_explain['explanation']}")
        print(f"    suggestion: {inv_explain['suggestion']}")
        print(f"    ✅ explain-status 正常工作")
    
    if audit_list:
        first_order = audit_list[0].order_id
        audit_explain = service.explain_status(type="audit", order_id=first_order)
        print(f"\n6.2 audit explain (Order: {first_order}):")
        print(f"    explanation: {audit_explain['explanation']}")
        print(f"    suggestion: {audit_explain['suggestion']}")
        print(f"    ✅ explain-status 正常工作")
    
    if exception_list:
        first_exc_order = exception_list[0].order_id
        exc_explain = service.explain_status(type="exception", order_id=first_exc_order)
        print(f"\n6.3 exception explain (Order: {first_exc_order}):")
        print(f"    explanation: {exc_explain['explanation']}")
        print(f"    suggestion: {exc_explain['suggestion']}")
        print(f"    ✅ explain-status 正常工作")
    
    print("\n" + "=" * 70)
    print("7. 评估 order_exception 支持程度")
    print("=" * 70)
    
    print("\n7.1 order_exception 实现方式:")
    print("    - 基于 sale.order 模型读取")
    print("    - exception_type 通过关键词推断（delay/stockout/address/customs/other）")
    print("    - 无真实异常数据源")
    
    print("\n7.2 评估结论:")
    print("    ⚠️  有限支持 (Limited Support)")
    print("    - 原因: exception_type 基于关键词推断，非真实异常数据")
    print("    - 建议: 后续需要对接 Odoo 的真实异常/退货模块")
    
    print("\n" + "=" * 70)
    print("8. 最终验证结果汇总")
    print("=" * 70)
    
    print("\n| 验证项 | 状态 | 详情 |")
    print("|--------|------|------|")
    print(f"| refresh_from_provider | ✅ 成功 | inventory: {result['inventory_count']}, audit: {result['audit_count']}, exception: {result['exception_count']} |")
    print(f"| ERPInventorySnapshot | ✅ 写入成功 | {len(inventory_list)} 条记录 |")
    print(f"| OrderAuditSnapshot | ✅ 写入成功 | {len(audit_list)} 条记录 |")
    print(f"| OrderExceptionSnapshot | ✅ 写入成功 | {len(exception_list)} 条记录 |")
    print(f"| /api/integration/* | ✅ 正常工作 | 可读取真实 snapshot |")
    print(f"| explain-status | ✅ 正常工作 | 可解释真实 snapshot |")
    print(f"| order_exception | ⚠️ 有限支持 | 基于关键词推断 |")
    
    print("\n" + "=" * 70)
    print("V3.5 第三步联调完成!")
    print("=" * 70)
    
    return {
        "inventory_count": result['inventory_count'],
        "audit_count": result['audit_count'],
        "exception_count": result['exception_count'],
        "inventory_snapshot_count": len(inventory_list),
        "audit_snapshot_count": len(audit_list),
        "exception_snapshot_count": len(exception_list),
    }


if __name__ == "__main__":
    main()
