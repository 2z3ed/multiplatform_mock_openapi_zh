"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Conversation {
  id: string;
  platform: string;
  customer_nick: string;
  status: string;
  assigned_agent: string | null;
  unread_count: number;
  last_message_time: string;
}

const platformLabels: Record<string, string> = {
  jd: "京东",
  taobao: "淘宝",
  douyin_shop: "抖音",
  wecom_kf: "企微",
};

const statusLabels: Record<string, string> = {
  active: "进行中",
  waiting: "等待中",
  closed: "已结束",
};

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchConversations() {
      try {
        const res = await fetch("/api/conversations");
        const data = await res.json();
        setConversations(data.items || []);
      } catch (error) {
        console.error("Failed to fetch conversations:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchConversations();
  }, []);

  if (loading) return <div className="p-8 text-center">加载中...</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 px-4">
          <h1 className="text-xl font-bold">会话列表</h1>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4">
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">平台</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">客户</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">未读</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">最后消息</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {conversations.map((conv) => (
                <tr key={conv.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                      {platformLabels[conv.platform] || conv.platform}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">{conv.customer_nick}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 py-1 text-xs font-medium rounded ${
                        conv.status === "active"
                          ? "bg-green-100 text-green-800"
                          : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {statusLabels[conv.status] || conv.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {conv.unread_count > 0 && (
                      <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">
                        {conv.unread_count}
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {conv.last_message_time ? new Date(conv.last_message_time).toLocaleString("zh-CN") : "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link
                      href={`/conversations/${conv.id}`}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      查看
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}