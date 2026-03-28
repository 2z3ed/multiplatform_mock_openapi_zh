"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  FollowUpTask,
  getAllFollowupTasks,
  executeFollowupTask,
  closeFollowupTask,
  getTaskTypeLabel,
  getStatusLabel,
} from "../lib/followup";

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  completed: "bg-green-100 text-green-800",
  closed: "bg-gray-100 text-gray-800",
};

const priorityColors: Record<string, string> = {
  low: "text-gray-500",
  medium: "text-yellow-600",
  high: "text-red-600",
};

export default function FollowupsPage() {
  const [tasks, setTasks] = useState<FollowUpTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [operatingId, setOperatingId] = useState<number | null>(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await getAllFollowupTasks(1, 50);
      setTasks(response.items);
    } catch (err) {
      setError("跟进任务加载失败");
      console.error("Failed to fetch followup tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async (taskId: number) => {
    try {
      setOperatingId(taskId);
      await executeFollowupTask(taskId);
      await fetchTasks();
    } catch (err) {
      alert(`执行失败: ${err instanceof Error ? err.message : "未知错误"}`);
    } finally {
      setOperatingId(null);
    }
  };

  const handleClose = async (taskId: number) => {
    try {
      setOperatingId(taskId);
      await closeFollowupTask(taskId);
      await fetchTasks();
    } catch (err) {
      alert(`关闭失败: ${err instanceof Error ? err.message : "未知错误"}`);
    } finally {
      setOperatingId(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto py-4 px-4">
            <div className="flex items-center justify-between">
              <h1 className="text-xl font-bold">跟进任务</h1>
              <Link
                href="/conversations"
                className="text-sm text-blue-600 hover:underline"
              >
                返回会话列表
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
              <h1 className="text-xl font-bold">跟进任务</h1>
              <Link
                href="/conversations"
                className="text-sm text-blue-600 hover:underline"
              >
                返回会话列表
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
            <h1 className="text-xl font-bold">跟进任务</h1>
            <Link
              href="/conversations"
              className="text-sm text-blue-600 hover:underline"
            >
              返回会话列表
            </Link>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto py-6 px-4">
        {tasks.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500">暂无跟进任务</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    任务
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    类型
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    优先级
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    状态
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-gray-900">
                        {task.title}
                      </div>
                      {task.description && (
                        <div className="text-sm text-gray-500">
                          {task.description}
                        </div>
                      )}
                      {task.suggested_copy && (
                        <div className="text-xs text-gray-400 mt-1">
                          话术: {task.suggested_copy}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-500">
                        {getTaskTypeLabel(task.task_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm ${priorityColors[task.priority] || "text-gray-500"}`}>
                        {task.priority === "high" ? "高" : task.priority === "medium" ? "中" : "低"}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`px-2 py-1 text-xs font-medium rounded ${
                          statusColors[task.status] || "bg-gray-100"
                        }`}
                      >
                        {getStatusLabel(task.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {task.status === "pending" && (
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleExecute(task.id)}
                            disabled={operatingId === task.id}
                            className="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 disabled:opacity-50"
                          >
                            {operatingId === task.id ? "处理中..." : "执行"}
                          </button>
                          <button
                            onClick={() => handleClose(task.id)}
                            disabled={operatingId === task.id}
                            className="px-3 py-1 bg-gray-500 text-white text-xs rounded hover:bg-gray-600 disabled:opacity-50"
                          >
                            {operatingId === task.id ? "处理中..." : "关闭"}
                          </button>
                        </div>
                      )}

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
