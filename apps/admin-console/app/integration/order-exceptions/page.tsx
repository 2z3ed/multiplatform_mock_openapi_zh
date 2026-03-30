"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface OrderExceptionSnapshot {
  id: number;
  order_id: string;
  platform: string;
  exception_type: string;
  exception_status: string;
  snapshot_at: string | null;
}

export default function OrderExceptionsPage() {
  const [items, setItems] = useState<OrderExceptionSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("/api/integration/order-exceptions");
      if (!response.ok) {
        throw new Error("Failed to fetch order exceptions");
      }
      const data = await response.json();
      setItems(data);
    } catch (err) {
      setError("异常订单数据加载失败");
      console.error("Failed to fetch order exceptions:", err);
    } finally {
      setLoading(false);
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "delay":
        return "bg-yellow-100 text-yellow-800";
      case "stockout":
        return "bg-red-100 text-red-800";
      case "address":
        return "bg-blue-100 text-blue-800";
      case "customs":
        return "bg-purple-100 text-purple-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case "delay":
        return "物流延误";
      case "stockout":
        return "缺货";
      case "address":
        return "地址问题";
      case "customs":
        return "清关问题";
      case "other":
        return "其他";
      default:
        return type;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "open":
        return "bg-red-100 text-red-800";
      case "processing":
        return "bg-yellow-100 text-yellow-800";
      case "resolved":
        return "bg-green-100 text-green-800";
      case "cancelled":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "open":
        return "待处理";
      case "processing":
        return "处理中";
      case "resolved":
        return "已解决";
      case "cancelled":
        return "已取消";
      default:
        return status;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-4 px-4">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold">异常订单</h1>
              <Link href="/" className="text-sm text-blue-600 hover:underline">
                返回首页
              </Link>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto py-6 px-4">
          <p className="text-gray-500">加载中...</p>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-4 px-4">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold">异常订单</h1>
              <Link href="/" className="text-sm text-blue-600 hover:underline">
                返回首页
              </Link>
            </div>
          </div>
        </header>
        <main className="max-w-7xl mx-auto py-6 px-4">
          <p className="text-red-500">{error}</p>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 px-4">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold">异常订单</h1>
            <Link href="/" className="text-sm text-blue-600 hover:underline">
              返回首页
            </Link>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4">
        {items.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500">暂无异常订单数据</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">订单ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">平台</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">异常类型</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">快照时间</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.order_id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.platform}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getTypeColor(item.exception_type)}`}>
                        {getTypeLabel(item.exception_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(item.exception_status)}`}>
                        {getStatusLabel(item.exception_status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.snapshot_at || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
