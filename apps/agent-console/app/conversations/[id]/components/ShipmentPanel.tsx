import type { Shipment } from "../types";

export default function ShipmentPanel({ shipment, platform }: { shipment: Shipment | null; platform?: string }) {
  if (!shipment || !shipment.shipments?.length) return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">物流信息</h3>
      <p className="text-sm text-gray-500">
        {platform === "wecom_kf" ? "当前平台暂不支持物流信息" : platform === "douyin_shop" ? "当前平台暂不支持物流查询" : "暂无物流信息"}
      </p>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">物流信息</h3>
      {shipment.shipments.map((ship, idx) => (
        <div key={idx} className="space-y-2 text-sm mb-3 last:mb-0">
          <div className="flex justify-between">
            <span className="text-gray-500">快递:</span>
            <span>{ship.express_company}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">单号:</span>
            <span>{ship.express_no}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">状态:</span>
            <span>{ship.status_name}</span>
          </div>
          {ship.trace.length > 0 && (
            <div className="mt-2 pt-2 border-t">
              <p className="text-gray-500 mb-1">最新物流:</p>
              <p className="text-xs text-gray-600">
                {ship.trace[0].message}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {ship.trace[0].time ? new Date(ship.trace[0].time).toLocaleString("zh-CN") : ""}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
