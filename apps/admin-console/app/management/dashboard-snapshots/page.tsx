"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface DashboardSnapshot {
  id: number;
  snapshot_date: string;
  metric_type: string;
  metric_value: number;
  created_at: string | null;
}

export default function DashboardSnapshotsPage() {
  const [items, setItems] = useState<DashboardSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("/api/management/dashboard-snapshots");
      if (!response.ok) {
        throw new Error("Failed to fetch dashboard snapshots");
      }
      const data = await response.json();
      setItems(data);
    } catch (err) {
      setError("管理看板快照数据加载失败");
      console.error("Failed to fetch dashboard snapshots:", err);
    } finally {
      setLoading(false);
    }
  };

  const getMetricTypeLabel = (type: string) => {
    switch (type) {
      case "conversation_count":
        return "会话数量";
      case "avg_response_time":
        return "平均响应时间";
      case "satisfaction_score":
        return "满意度评分";
      case "resolved_case_count":
        return "解决案例数";
      default:
        return type;
    }
  };

  const getMetricTypeColor = (type: string) => {
    switch (type) {
      case "conversation_count":
        return "bg-blue-100 text-blue-800";
      case "avg_response_time":
        return "bg-yellow-100 text-yellow-800";
      case "satisfaction_score":
        return "bg-green-100 text-green-800";
      case "resolved_case_count":
        return "bg-purple-100 text-purple-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-4 px-4">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold">管理看板快照</h1>
              <Link href="/" className="text-sm text-blue-600 hover:underline">返回首页</Link>
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
              <h1 className="text-xl font-bold">管理看板快照</h1>
              <Link href="/" className="text-sm text-blue-600 hover:underline">返回首页</Link>
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
            <h1 className="text-xl font-bold">管理看板快照</h1>
            <Link href="/" className="text-sm text-blue-600 hover:underline">返回首页</Link>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4">
        {items.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500">暂无管理看板快照数据</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">快照日期</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">指标类型</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">指标值</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.snapshot_date}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getMetricTypeColor(item.metric_type)}`}>
                        {getMetricTypeLabel(item.metric_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.metric_value}</td>
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
