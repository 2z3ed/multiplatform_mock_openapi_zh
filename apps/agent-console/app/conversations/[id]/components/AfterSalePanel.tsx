import type { AfterSale } from "../types";

export default function AfterSalePanel({ afterSales, platform }: { afterSales: AfterSale[]; platform?: string }) {
  if (!afterSales || afterSales.length === 0) return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">售后信息</h3>
      <p className="text-sm text-gray-500">
        {platform === "wecom_kf" ? "当前平台暂不支持售后信息" : "暂无售后信息"}
      </p>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">售后信息 ({afterSales.length})</h3>
      {afterSales.map((as, idx) => (
        <div key={idx} className="space-y-2 text-sm mb-3 last:mb-0">
          <div className="flex justify-between">
            <span className="text-gray-500">售后单号:</span>
            <span>{as.after_sale_id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">类型:</span>
            <span>{as.type_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">状态:</span>
            <span>{as.status_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">金额:</span>
            <span>¥{as.apply_amount}</span>
          </div>
          {as.reason && (
            <div className="mt-2 pt-2 border-t">
              <p className="text-gray-500 mb-1">原因:</p>
              <p className="text-xs text-gray-600">{as.reason}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
