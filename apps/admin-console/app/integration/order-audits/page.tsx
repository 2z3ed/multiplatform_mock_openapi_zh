"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface OrderAuditSnapshot {
  id: number;
  order_id: string;
  platform: string;
  audit_status: string;
  audit_reason: string | null;
  snapshot_at: string | null;
}

export default function OrderAuditsPage() {
  const [items, setItems] = useState<OrderAuditSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("/api/integration/order-audits");
      if (!response.ok) {
        throw new Error("Failed to fetch order audits");
      }
      const data = await response.json();
      setItems(data);
    } catch (err) {
      setError("订单审核数据加载失败");
      console.error("Failed to fetch order audits:", err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "approved":
        return "bg-green-100 text-green-800";
      case "rejected":
        return "bg-red-100 text-red-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "approved":
        return "已通过";
      case "rejected":
        return "已拒绝";
      case "pending":
        return "待审核";
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
              <h1 className="text-xl font-bold">订单审核状态</h1>
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
              <h1 className="text-xl font-bold">订单审核状态</h1>
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
            <h1 className="text-xl font-bold">订单审核状态</h1>
            <Link href="/" className="text-sm text-blue-600 hover:underline">
              返回首页
            </Link>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4">
        {items.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500">暂无订单审核数据</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">订单ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">平台</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">审核状态</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">审核原因</th>
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
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(item.audit_status)}`}>
                        {getStatusLabel(item.audit_status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.audit_reason || "-"}</td>
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
