"""
V3.5 第三步真实数据库刷新脚本
使用真实 PostgreSQL 数据库执行 refresh_from_provider
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'providers'))
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'shared-db'))
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'domain-models'))
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'provider-sdk'))
sys.path.insert(0, os.path.join(BASE_DIR, 'packages', 'shared-config'))
sys.path.insert(0, os.path.join(BASE_DIR, 'apps', 'domain-service'))

from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

from shared_db import SessionLocal
from app.services.integration_service import IntegrationService
from app.repositories.erp_inventory_snapshot_repository import ERPInventorySnapshotRepository
from app.repositories.order_audit_snapshot_repository import OrderAuditSnapshotRepository
from app.repositories.order_exception_snapshot_repository import OrderExceptionSnapshotRepository
from app.repositories.integration_sync_status_repository import IntegrationSyncStatusRepository

from odoo.real.client import OdooClient
from odoo.real.provider import OdooRealProvider


def main():
    print("=" * 70)
    print("V3.5 第三步真实数据库刷新")
    print("=" * 70)
    
    print(f"\n配置信息:")
    print(f"  ODOO_BASE_URL: {os.getenv('ODOO_BASE_URL')}")
    print(f"  ODOO_DB: {os.getenv('ODOO_DB')}")
    print(f"  ODOO_PROVIDER_MODE: {os.getenv('ODOO_PROVIDER_MODE')}")
    print(f"  DATABASE_URL: {os.getenv('DATABASE_URL')}")
    
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
    print("2. 连接真实 PostgreSQL 数据库")
    print("=" * 70)
    
    db_session = SessionLocal()
    print(f"✅ 数据库连接成功")
    
    print("\n" + "=" * 70)
    print("3. 执行 refresh_from_provider")
    print("=" * 70)
    
    service = IntegrationService(db_session, odoo_provider=provider)
    result = service.refresh_from_provider(trigger_type="manual")
    db_session.commit()
    
    print(f"✅ refresh_from_provider 完成!")
    print(f"   - inventory_count: {result['inventory_count']}")
    print(f"   - audit_count: {result['audit_count']}")
    print(f"   - exception_count: {result['exception_count']}")
    print(f"   - message: {result['message']}")
    
    print("\n" + "=" * 70)
    print("4. 验证 Snapshot 写入")
    print("=" * 70)
    
    inventory_repo = ERPInventorySnapshotRepository(db_session)
    audit_repo = OrderAuditSnapshotRepository(db_session)
    exception_repo = OrderExceptionSnapshotRepository(db_session)
    sync_status_repo = IntegrationSyncStatusRepository(db_session)
    
    inventory_list = inventory_repo.list_all()
    print(f"\n4.1 ERPInventorySnapshot: {len(inventory_list)} 条")
    if inventory_list:
        for inv in inventory_list[:3]:
            print(f"    - SKU: {inv.sku_code}, Warehouse: {inv.warehouse_code}, Available: {inv.available_qty}")
    
    audit_list = audit_repo.list_all()
    print(f"\n4.2 OrderAuditSnapshot: {len(audit_list)} 条")
    if audit_list:
        for audit in audit_list[:3]:
            print(f"    - Order: {audit.order_id}, Platform: {audit.platform}, Status: {audit.audit_status}")
    
    exception_list = exception_repo.list_all()
    print(f"\n4.3 OrderExceptionSnapshot: {len(exception_list)} 条")
    if exception_list:
        for exc in exception_list[:3]:
            print(f"    - Order: {exc.order_id}, Type: {exc.exception_type}, Status: {exc.exception_status}")
    
    sync_status = sync_status_repo.get_latest()
    print(f"\n4.4 IntegrationSyncStatus:")
    if sync_status:
        print(f"    - ID: {sync_status.id}")
        print(f"    - provider_mode: {sync_status.provider_mode}")
        print(f"    - status: {sync_status.status}")
        print(f"    - inventory_count: {sync_status.inventory_count}")
        print(f"    - audit_count: {sync_status.audit_count}")
        print(f"    - exception_count: {sync_status.exception_count}")
    
    db_session.close()
    
    print("\n" + "=" * 70)
    print("V3.5 第三步真实数据库刷新完成!")
    print("=" * 70)
    
    return result


if __name__ == "__main__":
    main()
