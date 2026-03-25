"use client";

import { useState } from "react";

interface AuditLog {
  id: string;
  action: string;
  user: string;
  resource: string;
  timestamp: string;
  details: string;
}

const mockAuditLogs: AuditLog[] = [
  {
    id: "log_001",
    action: "platform_config_updated",
    user: "admin",
    resource: "jd",
    timestamp: "2024-03-20T10:00:00Z",
    details: "更新京东平台配置",
  },
  {
    id: "log_002",
    action: "provider_mode_switched",
    user: "admin",
    resource: "jd",
    timestamp: "2024-03-20T10:05:00Z",
    details: "切换为 mock 模式",
  },
  {
    id: "log_003",
    action: "document_uploaded",
    user: "admin",
    resource: "doc_001",
    timestamp: "2024-03-20T10:10:00Z",
    details: "上传文档: 订单查询FAQ",
  },
  {
    id: "log_004",
    action: "ai_suggestion_generated",
    user: "agent_001",
    resource: "conv_001",
    timestamp: "2024-03-20T10:15:00Z",
    details: "生成建议回复",
  },
  {
    id: "log_005",
    action: "message_sent",
    user: "agent_001",
    resource: "conv_001",
    timestamp: "2024-03-20T10:20:00Z",
    details: "发送消息给客户",
  },
  {
    id: "log_006",
    action: "conversation_assigned",
    user: "system",
    resource: "conv_001",
    timestamp: "2024-03-20T10:25:00Z",
    details: "分配会话给 agent_001",
  },
  {
    id: "log_007",
    action: "conversation_handed_off",
    user: "agent_001",
    resource: "conv_002",
    timestamp: "2024-03-20T10:30:00Z",
    details: "将会话转交给 agent_002",
  },
];

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
  const [logs] = useState<AuditLog[]>(mockAuditLogs);
  const [actionFilter, setActionFilter] = useState("");

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

        <div className="bg-white shadow rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">资源</th>
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
                  <td className="px-6 py-4 whitespace-nowrap">{log.user}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{log.resource}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.details}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(log.timestamp).toLocaleString("zh-CN")}
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