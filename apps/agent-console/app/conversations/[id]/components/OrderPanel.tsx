import type { Order } from "../types";

export default function OrderPanel({ order, platform }: { order: Order | null; platform?: string }) {
  if (!order) return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">订单信息</h3>
      <p className="text-sm text-gray-500">
        {platform === "wecom_kf" ? "当前平台暂不支持订单上下文" : "暂无订单信息"}
      </p>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">订单信息</h3>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">订单号:</span>
          <span>{order.order_id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">状态:</span>
          <span>{order.status_name}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">金额:</span>
          <span>¥{order.payment_amount}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">收货人:</span>
          <span>{order.receiver_name || "-"}</span>
        </div>
        {order.receiver_address?.city && (
          <div className="flex justify-between">
            <span className="text-gray-500">收货地:</span>
            <span>{order.receiver_address.city}{order.receiver_address.district || ""}</span>
          </div>
        )}
        <div className="mt-3 pt-3 border-t">
          <p className="text-gray-500 mb-1">商品:</p>
          {(order.items || []).map((item, idx) => (
            <p key={idx} className="text-sm">
              {item.sku_name} x{item.quantity}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}
