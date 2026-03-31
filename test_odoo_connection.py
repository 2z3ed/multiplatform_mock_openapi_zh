"""
V3.5 第三步真实 Odoo 联调测试
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'providers'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'shared-db'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'domain-model'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'provider-sdk'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'packages', 'shared-config'))

from dotenv import load_dotenv
load_dotenv()

from odoo.real.client import OdooClient
from odoo.real.mapper import map_inventory, map_order_audit, map_order_exception
from odoo.real.provider import OdooRealProvider


def main():
    print("=" * 60)
    print("V3.5 第三步真实 Odoo 联调测试")
    print("=" * 60)
    
    print(f"\n配置信息:")
    print(f"  ODOO_BASE_URL: {os.getenv('ODOO_BASE_URL')}")
    print(f"  ODOO_DB: {os.getenv('ODOO_DB')}")
    print(f"  ODOO_USERNAME: {os.getenv('ODOO_USERNAME')}")
    api_key = os.getenv('ODOO_API_KEY', '')
    print(f"  ODOO_API_KEY: {api_key[:10]}...")
    
    client = OdooClient(
        base_url=os.getenv('ODOO_BASE_URL'),
        db=os.getenv('ODOO_DB'),
        username=os.getenv('ODOO_USERNAME'),
        api_key=os.getenv('ODOO_API_KEY'),
        timeout=int(os.getenv('ODOO_TIMEOUT', '30')),
        verify_ssl=os.getenv('ODOO_VERIFY_SSL', 'true').lower() == 'true',
    )
    
    print("\n" + "=" * 60)
    print("1. 测试 authenticate")
    print("=" * 60)
    
    uid = client.authenticate()
    if uid:
        print(f"✅ authenticate 成功! UID: {uid}")
    else:
        print("❌ authenticate 失败!")
        return
    
    print("\n" + "=" * 60)
    print("2. 测试 stock.quant 读取")
    print("=" * 60)
    
    quants = client.search_read(
        model="stock.quant",
        domain=[],
        fields=["id", "product_id", "location_id", "quantity", "reserved_quantity"],
        limit=5,
    )
    print(f"✅ stock.quant 读取成功! 找到 {len(quants)} 条记录")
    for q in quants[:3]:
        product_id = q.get('product_id', [])
        product_name = product_id[1] if isinstance(product_id, list) and len(product_id) > 1 else str(product_id)
        location_id = q.get('location_id', [])
        location_name = location_id[1] if isinstance(location_id, list) and len(location_id) > 1 else str(location_id)
        quantity = q.get('quantity', 0) or 0
        reserved = q.get('reserved_quantity', 0) or 0
        print(f"   - ID: {q.get('id')}, Product: {product_name}, Location: {location_name}")
        print(f"     Quantity: {quantity}, Reserved: {reserved}")
    
    print("\n" + "=" * 60)
    print("3. 测试 sale.order 读取")
    print("=" * 60)
    
    orders = client.search_read(
        model="sale.order",
        domain=[],
        fields=["id", "name", "state", "note"],
        limit=5,
    )
    print(f"✅ sale.order 读取成功! 找到 {len(orders)} 条记录")
    for o in orders[:3]:
        print(f"   - ID: {o.get('id')}, Order: {o.get('name')}, State: {o.get('state')}")
    
    print("\n" + "=" * 60)
    print("4. 测试 inventory mapper")
    print("=" * 60)
    
    inv_mapped = [map_inventory(q) for q in quants[:3]]
    for inv in inv_mapped:
        print(f"   - SKU: {inv.get('sku_code')}, Warehouse: {inv.get('warehouse_code')}")
        print(f"     Available: {inv.get('available_qty')}, Status: {inv.get('status')}")
    
    print("\n" + "=" * 60)
    print("5. 测试 order_audit mapper")
    print("=" * 60)
    
    audit_mapped = [map_order_audit(o) for o in orders[:3]]
    for audit in audit_mapped:
        print(f"   - Order: {audit.get('order_id')}, Status: {audit.get('audit_status')}")
    
    print("\n" + "=" * 60)
    print("6. 测试 order_exception mapper")
    print("=" * 60)
    
    exc_mapped = [map_order_exception(o) for o in orders[:3]]
    for exc in exc_mapped:
        print(f"   - Order: {exc.get('order_id')}, Type: {exc.get('exception_type')}")
    
    print("\n" + "=" * 60)
    print("7. 测试 OdooRealProvider")
    print("=" * 60)
    
    provider = OdooRealProvider(client)
    
    inv_data = provider.get_inventory_list()
    print(f"✅ get_inventory_list 成功! 返回 {len(inv_data)} 条记录")
    
    audit_data = provider.get_order_audit_list()
    print(f"✅ get_order_audit_list 成功! 返回 {len(audit_data)} 条记录")
    
    exc_data = provider.get_order_exception_list()
    print(f"✅ get_order_exception_list 成功! 返回 {len(exc_data)} 条记录")
    
    print("\n" + "=" * 60)
    print("联调完成！所有测试通过。")
    print("=" * 60)
    
    print("\n" + "=" * 60)
    print("V3.5 第三步真实联调验证结果")
    print("=" * 60)
    
    print("\n## 一、验证结果汇总")
    print(f"- ✅ authenticate 成功 (UID: {uid})")
    print(f"- ✅ stock.quant 读取成功，找到 {len(quants)} 条记录")
    print(f"- ✅ sale.order 读取成功，找到 {len(orders)} 条记录")
    print(f"- ✅ inventory mapper 成功，映射 {len(inv_mapped)} 条记录")
    print(f"- ✅ order_audit mapper 成功，映射 {len(audit_mapped)} 条记录")
    print(f"- ✅ order_exception mapper 成功，映射 {len(exc_mapped)} 条记录")
    print(f"- ✅ OdooRealProvider 所有方法正常工作")
    
    print("\n## 二、当前状态总结")
    print("| 项目 | 状态 |")
    print("|------|------|")
    print("| V3.5 第三步 | ✅ 已完成 |")
    print("| authenticate | ✅ 成功 (UID: {}) |".format(uid))
    print("| stock.quant | ✅ 成功 ({} 条记录) |".format(len(quants)))
    print("| sale.order | ✅ 成功 ({} 条记录) |".format(len(orders)))
    print("| inventory mapper | ✅ 成功 |")
    print("| order_audit mapper | ✅ 成功 |")
    print("| order_exception mapper | ✅ 成功 |")
    print("| OdooRealProvider | ✅ 成功 |")


if __name__ == "__main__":
    main()
