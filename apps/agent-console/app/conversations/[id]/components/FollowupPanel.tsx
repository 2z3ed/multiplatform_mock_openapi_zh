"use client";

import { useState, useEffect } from "react";
import {
  FollowUpTask,
  getFollowupTasksByConversationId,
  executeFollowupTask,
  closeFollowupTask,
  getTaskTypeLabel,
  getStatusLabel,
} from "../../../lib/followup";

interface FollowupPanelProps {
  conversationPk: number;
}

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  completed: "bg-green-100 text-green-800",
  closed: "bg-gray-100 text-gray-800",
};

export default function FollowupPanel({ conversationPk }: FollowupPanelProps) {
  const [tasks, setTasks] = useState<FollowUpTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [operatingId, setOperatingId] = useState<number | null>(null);

  useEffect(() => {
    fetchTasks();
  }, [conversationPk]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getFollowupTasksByConversationId(conversationPk);
      setTasks(data);
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
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">跟进任务</h3>
        <p className="text-sm text-gray-500">加载中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">跟进任务</h3>
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">跟进任务</h3>
        <p className="text-sm text-gray-500">暂无跟进任务</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">跟进任务</h3>
      <div className="space-y-3">
        {tasks.map((task) => (
          <div key={task.id} className="border rounded p-3 text-sm">
            <div className="flex justify-between items-start mb-2">
              <div>
                <span className="font-medium">{task.title}</span>
                <span className="ml-2 text-xs text-gray-500">
                  {getTaskTypeLabel(task.task_type)}
                </span>
              </div>
              <span
                className={`px-2 py-0.5 text-xs rounded ${
                  statusColors[task.status] || "bg-gray-100"
                }`}
              >
                {getStatusLabel(task.status)}
              </span>
            </div>
            {task.description && (
              <p className="text-gray-600 mb-2">{task.description}</p>
            )}
            {task.suggested_copy && (
              <div className="bg-gray-50 p-2 rounded mb-2">
                <p className="text-xs text-gray-500">建议话术:</p>
                <p className="text-sm">{task.suggested_copy}</p>
              </div>
            )}
            {task.due_date && (
              <p className="text-xs text-gray-500 mb-2">
                截止: {new Date(task.due_date).toLocaleString("zh-CN")}
              </p>
            )}
            <div className="flex gap-2">
              {task.status === "pending" && (
                <>
                  <button
                    onClick={() => handleExecute(task.id)}
                    disabled={operatingId === task.id}
                    className="px-2 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 disabled:opacity-50"
                  >
                    {operatingId === task.id ? "执行中..." : "执行"}
                  </button>
                  <button
                    onClick={() => handleClose(task.id)}
                    disabled={operatingId === task.id}
                    className="px-2 py-1 bg-gray-500 text-white text-xs rounded hover:bg-gray-600 disabled:opacity-50"
                  >
                    {operatingId === task.id ? "处理中..." : "关闭"}
                  </button>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
