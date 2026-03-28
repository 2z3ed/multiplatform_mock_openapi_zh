"use client";

import { useState, useEffect } from "react";
import {
  RiskFlag,
  getRiskFlagsByCustomerId,
  createRiskFlag,
  resolveRiskFlag,
  dismissRiskFlag,
  getRiskTypeLabel,
  getRiskLevelLabel,
  getStatusLabel,
} from "../../../lib/riskFlag";

interface RiskFlagPanelProps {
  customerPk: number;
  conversationPk?: number;
}

const statusColors: Record<string, string> = {
  active: "bg-red-100 text-red-800",
  resolved: "bg-green-100 text-green-800",
  dismissed: "bg-gray-100 text-gray-800",
};

export default function RiskFlagPanel({ customerPk, conversationPk }: RiskFlagPanelProps) {
  const [riskFlags, setRiskFlags] = useState<RiskFlag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [operatingId, setOperatingId] = useState<number | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    fetchRiskFlags();
  }, [customerPk]);

  const fetchRiskFlags = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getRiskFlagsByCustomerId(customerPk);
      setRiskFlags(data);
    } catch (err) {
      setError("风险标记加载失败");
      console.error("Failed to fetch risk flags:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (riskFlagId: number) => {
    try {
      setOperatingId(riskFlagId);
      await resolveRiskFlag(riskFlagId);
      await fetchRiskFlags();
    } catch (err) {
      alert(`处理失败: ${err instanceof Error ? err.message : "未知错误"}`);
    } finally {
      setOperatingId(null);
    }
  };

  const handleDismiss = async (riskFlagId: number) => {
    try {
      setOperatingId(riskFlagId);
      await dismissRiskFlag(riskFlagId);
      await fetchRiskFlags();
    } catch (err) {
      alert(`忽略失败: ${err instanceof Error ? err.message : "未知错误"}`);
    } finally {
      setOperatingId(null);
    }
  };

  const handleCreate = async (riskType: string, riskLevel: string, description: string) => {
    try {
      setCreating(true);
      await createRiskFlag({
        customer_id: customerPk,
        conversation_id: conversationPk,
        risk_type: riskType,
        risk_level: riskLevel || "low",
        description: description || undefined,
      });
      setShowCreateForm(false);
      await fetchRiskFlags();
    } catch (err) {
      alert(`创建失败: ${err instanceof Error ? err.message : "未知错误"}`);
    } finally {
      setCreating(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">风险标记</h3>
        <p className="text-sm text-gray-500">加载中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">风险标记</h3>
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="font-medium text-lg">风险标记</h3>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="text-xs text-blue-600 hover:underline"
        >
          {showCreateForm ? "取消" : "+ 创建"}
        </button>
      </div>

      {showCreateForm && (
        <RiskFlagCreateForm
          onSubmit={handleCreate}
          onCancel={() => setShowCreateForm(false)}
          submitting={creating}
        />
      )}

      {riskFlags.length === 0 && !showCreateForm ? (
        <p className="text-sm text-gray-500">暂无风险标记</p>
      ) : (
        <div className="space-y-3">
          {riskFlags.map((flag) => (
            <div key={flag.id} className="border rounded p-3 text-sm">
              <div className="flex justify-between items-start mb-2">
                <div>
                  <span className="font-medium">{getRiskTypeLabel(flag.risk_type)}</span>
                  <span className="ml-2 text-xs text-gray-500">
                    {getRiskLevelLabel(flag.risk_level)}
                  </span>
                </div>
                <span
                  className={`px-2 py-0.5 text-xs rounded ${
                    statusColors[flag.status] || "bg-gray-100"
                  }`}
                >
                  {getStatusLabel(flag.status)}
                </span>
              </div>
              {flag.description && (
                <p className="text-gray-600 mb-2">{flag.description}</p>
              )}
              {flag.created_at && (
                <p className="text-xs text-gray-500 mb-2">
                  创建于: {new Date(flag.created_at).toLocaleString("zh-CN")}
                </p>
              )}
              {flag.status === "active" && (
                <div className="flex gap-2">
                  <button
                    onClick={() => handleResolve(flag.id)}
                    disabled={operatingId === flag.id}
                    className="px-2 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 disabled:opacity-50"
                  >
                    {operatingId === flag.id ? "处理中..." : "处理"}
                  </button>
                  <button
                    onClick={() => handleDismiss(flag.id)}
                    disabled={operatingId === flag.id}
                    className="px-2 py-1 bg-gray-500 text-white text-xs rounded hover:bg-gray-600 disabled:opacity-50"
                  >
                    {operatingId === flag.id ? "处理中..." : "忽略"}
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function RiskFlagCreateForm({
  onSubmit,
  onCancel,
  submitting,
}: {
  onSubmit: (riskType: string, riskLevel: string, description: string) => void;
  onCancel: () => void;
  submitting: boolean;
}) {
  const [riskType, setRiskType] = useState("negative_sentiment");
  const [riskLevel, setRiskLevel] = useState("low");
  const [description, setDescription] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(riskType, riskLevel, description);
  };

  return (
    <form onSubmit={handleSubmit} className="border rounded p-3 mb-3 bg-gray-50">
      <div className="mb-2">
        <label className="block text-xs text-gray-500 mb-1">风险类型</label>
        <select
          value={riskType}
          onChange={(e) => setRiskType(e.target.value)}
          className="w-full border rounded px-2 py-1 text-sm"
        >
          <option value="negative_sentiment">负面情绪</option>
          <option value="complaint_tendency">投诉倾向</option>
        </select>
      </div>
      <div className="mb-2">
        <label className="block text-xs text-gray-500 mb-1">风险等级</label>
        <select
          value={riskLevel}
          onChange={(e) => setRiskLevel(e.target.value)}
          className="w-full border rounded px-2 py-1 text-sm"
        >
          <option value="low">低风险</option>
          <option value="medium">中风险</option>
          <option value="high">高风险</option>
        </select>
      </div>
      <div className="mb-2">
        <label className="block text-xs text-gray-500 mb-1">描述</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full border rounded px-2 py-1 text-sm"
          rows={2}
          placeholder="可选"
        />
      </div>
      <div className="flex gap-2">
        <button
          type="submit"
          disabled={submitting}
          className="px-3 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {submitting ? "创建中..." : "创建"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-3 py-1 bg-gray-500 text-white text-xs rounded hover:bg-gray-600"
        >
          取消
        </button>
      </div>
    </form>
  );
}
