"""
检查 Odoo 中可用的模型
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'providers'))

from dotenv import load_dotenv
load_dotenv()

from odoo.real.client import OdooClient

def main():
    client = OdooClient(
        base_url=os.getenv("ODOO_BASE_URL", "http://localhost:8069"),
        db=os.getenv("ODOO_DB", "odoo"),
        username=os.getenv("ODOO_USERNAME", ""),
        api_key=os.getenv("ODOO_API_KEY", ""),
    )
    
    uid = client.authenticate()
    print(f"UID: {uid}")
    
    print("\n检查常用模型是否存在:")
    
    models_to_check = [
        "stock.quant",
        "stock.location",
        "stock.warehouse",
        "sale.order",
        "sale.order.line",
        "product.product",
        "product.template",
        "res.partner",
        "res.users",
        "ir.model",
    ]
    
    for model in models_to_check:
        try:
            result = client.search_read(model=model, domain=[], fields=["id"], limit=1)
            print(f"  ✅ {model}: 存在 ({len(result)} 条记录)")
        except Exception as e:
            print(f"  ❌ {model}: {str(e)[:50]}")
    
    print("\n列出所有已安装的模型 (ir.model):")
    try:
        models = client.search_read(
            model="ir.model",
            domain=[],
            fields=["model", "name"],
            limit=100,
            order="model"
        )
        print(f"找到 {len(models)} 个模型:")
        for m in models[:50]:
            print(f"  - {m.get('model')}: {m.get('name')}")
    except Exception as e:
        print(f"  无法列出模型: {e}")

if __name__ == "__main__":
    main()
