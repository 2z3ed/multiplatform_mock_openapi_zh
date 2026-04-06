import { useState } from "react";
import type { Inventory } from "../types";

const stockStateLabels: Record<string, string> = {
  in_stock: "有货",
  low_stock: "低库存",
  out_of_stock: "缺货",
  pre_order: "预售",
};

function normalizeStockState(raw: string): string {
  const map: Record<string, string> = {
    "有货": "in_stock",
    "低库存": "low_stock",
    "紧张": "low_stock",
    "无货": "out_of_stock",
    "缺货": "out_of_stock",
    "预售": "pre_order",
  };
  return map[raw] || raw;
}

export default function InventoryPanel({ inventory, platform }: { inventory: Inventory | null; platform?: string }) {
  const [expanded, setExpanded] = useState(false);

  if (!inventory || !inventory.items?.length) return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">库存信息</h3>
      <p className="text-sm text-gray-500">
        {platform === "wecom_kf" ? "当前平台暂不支持库存信息" : "暂无库存信息"}
      </p>
    </div>
  );

  const items = inventory.items;
  const outOfStock = items.filter(i => normalizeStockState(i.stock_state) === "out_of_stock");
  const lowStock = items.filter(i => normalizeStockState(i.stock_state) === "low_stock");
  const inStock = items.filter(i => normalizeStockState(i.stock_state) === "in_stock");

  let overallLabel = "库存充足";
  let overallColor = "text-green-600";
  if (outOfStock.length > 0) {
    overallLabel = "存在缺货风险";
    overallColor = "text-red-600";
  } else if (lowStock.length > 0) {
    overallLabel = "存在低库存";
    overallColor = "text-yellow-600";
  }

  const sorted = [...items].sort((a, b) => {
    const order = { out_of_stock: 0, low_stock: 1, in_stock: 2 };
    return (order[normalizeStockState(a.stock_state) as keyof typeof order] ?? 3) - (order[normalizeStockState(b.stock_state) as keyof typeof order] ?? 3);
  });

  const displayItems = expanded ? sorted : sorted.slice(0, 5);

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">库存信息</h3>
      <div className="mb-3 p-2 bg-gray-50 rounded text-xs">
        <div className="flex justify-between items-center">
          <span className="text-gray-500">SKU 总数: {items.length}</span>
          <span className={`font-medium ${overallColor}`}>{overallLabel}</span>
        </div>
        <div className="flex gap-3 mt-1 text-gray-400">
          <span>有货 {inStock.length}</span>
          <span>低库存 {lowStock.length}</span>
          <span>缺货 {outOfStock.length}</span>
        </div>
      </div>
      {displayItems.map((item, idx) => {
        const ns = normalizeStockState(item.stock_state);
        return (
          <div key={idx} className="flex items-center justify-between py-1.5 text-xs border-b last:border-0">
            <div className="flex-1 min-w-0">
              <span className="font-medium truncate block">{item.product_name || item.sku_id}</span>
              {item.warehouse_name && (
                <span className="text-gray-400">{item.warehouse_name}</span>
              )}
            </div>
            <div className="flex items-center gap-2 ml-2 shrink-0">
              <span className={`px-1.5 py-0.5 rounded text-xs ${
                ns === "out_of_stock" ? "bg-red-100 text-red-700" :
                ns === "low_stock" ? "bg-yellow-100 text-yellow-700" :
                ns === "pre_order" ? "bg-gray-100 text-gray-700" :
                "bg-green-100 text-green-700"
              }`}>
                {stockStateLabels[ns] || ns}
              </span>
              <span className="text-gray-500 w-8 text-right">{item.quantity}</span>
            </div>
          </div>
        );
      })}
      {items.length > 5 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full mt-2 text-xs text-blue-600 hover:text-blue-800 py-1"
        >
          {expanded ? `收起` : `查看全部 ${items.length} 个 SKU`}
        </button>
      )}
    </div>
  );
}
