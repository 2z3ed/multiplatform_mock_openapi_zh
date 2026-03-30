"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface VOCTopic {
  id: number;
  topic_name: string;
  topic_type: string;
  source: string;
  occurrence_count: number;
  summary: string | null;
  created_at: string | null;
}

export default function VOCTopicsPage() {
  const [items, setItems] = useState<VOCTopic[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchItems();
  }, []);

  const fetchItems = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch("/api/management/voc-topics");
      if (!response.ok) {
        throw new Error("Failed to fetch VOC topics");
      }
      const data = await response.json();
      setItems(data);
    } catch (err) {
      setError("VOC 主题数据加载失败");
      console.error("Failed to fetch VOC topics:", err);
    } finally {
      setLoading(false);
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "complaint":
        return "bg-red-100 text-red-800";
      case "feedback":
        return "bg-blue-100 text-blue-800";
      case "suggestion":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getTypeLabel = (type: string) => {
    switch (type) {
      case "complaint":
        return "投诉";
      case "feedback":
        return "反馈";
      case "suggestion":
        return "建议";
      default:
        return type;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-4 px-4">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold">VOC 主题</h1>
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
              <h1 className="text-xl font-bold">VOC 主题</h1>
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
            <h1 className="text-xl font-bold">VOC 主题</h1>
            <Link href="/" className="text-sm text-blue-600 hover:underline">返回首页</Link>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4">
        {items.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500">暂无 VOC 主题数据</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">主题名称</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">来源</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">频次</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">摘要</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{item.id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.topic_name}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getTypeColor(item.topic_type)}`}>
                        {getTypeLabel(item.topic_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.source}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.occurrence_count}</td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{item.summary || "-"}</td>
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
