"use client";

import { useState, useEffect } from "react";

interface AuditLog {
  id: number;
  action: string;
  actor_type: string;
  actor_id: string | null;
  target_type: string | null;
  target_id: string | null;
  detail: string | null;
  detail_json: Record<string, unknown> | null;
  created_at: string;
}

const actionLabels: Record<string, string> = {
  platform_config_updated: "平台配置更新",
  provider_mode_switched: "Provider模式切换",
  document_uploaded: "文档上传",
  knowledge_reindexed: "知识库重建索引",
  ai_suggestion_generated: "AI建议生成",
  message_sent: "消息发送",
  conversation_assigned: "会话分配",
  conversation_handed_off: "会话转接",
};

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState("");

  useEffect(() => {
    async function fetchAuditLogs() {
      try {
        const res = await fetch("/api/audit-logs?limit=100");
        const data = await res.json();
        setLogs(data.items || []);
      } catch (error) {
        console.error("Failed to fetch audit logs:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchAuditLogs();
  }, []);

  const filteredLogs = actionFilter
    ? logs.filter((log) => log.action === actionFilter)
    : logs;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-4 px-4">
          <h1 className="text-xl font-bold">审计日志</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 px-4">
        <div className="mb-4">
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="">全部操作</option>
            {Object.entries(actionLabels).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {loading ? (
          <div className="text-center py-8">加载中...</div>
        ) : (
          <div className="bg-white shadow rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">对象</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">详情</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">
                        {actionLabels[log.action] || log.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">{log.actor_id || log.actor_type}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{log.target_id || "-"}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.detail || (log.detail_json ? JSON.stringify(log.detail_json).slice(0, 50) : "-")}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {log.created_at ? new Date(log.created_at).toLocaleString("zh-CN") : "-"}
                    </td>
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