"use client";

import { useState, useEffect } from "react";
import {
  Recommendation,
  getRecommendationsByConversationId,
  acceptRecommendation,
  rejectRecommendation,
  getStatusLabel,
} from "../../../lib/recommendation";

interface RecommendationPanelProps {
  conversationPk: number;
}

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-800",
  accepted: "bg-green-100 text-green-800",
  rejected: "bg-gray-100 text-gray-800",
};

export default function RecommendationPanel({ conversationPk }: RecommendationPanelProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [operatingId, setOperatingId] = useState<number | null>(null);

  useEffect(() => {
    fetchRecommendations();
  }, [conversationPk]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getRecommendationsByConversationId(conversationPk);
      setRecommendations(data);
    } catch (err) {
      setError("推荐记录加载失败");
      console.error("Failed to fetch recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (recommendationId: number) => {
    try {
      setOperatingId(recommendationId);
      await acceptRecommendation(recommendationId);
      await fetchRecommendations();
    } catch (err) {
      alert(`接受失败: ${err instanceof Error ? err.message : "未知错误"}`);
    } finally {
      setOperatingId(null);
    }
  };

  const handleReject = async (recommendationId: number) => {
    try {
      setOperatingId(recommendationId);
      await rejectRecommendation(recommendationId);
      await fetchRecommendations();
    } catch (err) {
      alert(`拒绝失败: ${err instanceof Error ? err.message : "未知错误"}`);
    } finally {
      setOperatingId(null);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">推荐商品</h3>
        <p className="text-sm text-gray-500">加载中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">推荐商品</h3>
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">推荐商品</h3>
        <p className="text-sm text-gray-500">暂无推荐记录</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">推荐商品</h3>
      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div key={rec.id} className="border rounded p-3 text-sm">
            <div className="flex justify-between items-start mb-2">
              <div>
                <span className="font-medium">{rec.product_name}</span>
                <span className="ml-2 text-xs text-gray-500">
                  ID: {rec.product_id}
                </span>
              </div>
              <span
                className={`px-2 py-0.5 text-xs rounded ${
                  statusColors[rec.status] || "bg-gray-100"
                }`}
              >
                {getStatusLabel(rec.status)}
              </span>
            </div>
            {rec.reason && (
              <p className="text-gray-600 mb-2">推荐理由: {rec.reason}</p>
            )}
            {rec.suggested_copy && (
              <div className="bg-gray-50 p-2 rounded mb-2">
                <p className="text-xs text-gray-500">推荐话术:</p>
                <p className="text-sm">{rec.suggested_copy}</p>
              </div>
            )}
            {rec.status === "pending" && (
              <div className="flex gap-2">
                <button
                  onClick={() => handleAccept(rec.id)}
                  disabled={operatingId === rec.id}
                  className="px-2 py-1 bg-green-500 text-white text-xs rounded hover:bg-green-600 disabled:opacity-50"
                >
                  {operatingId === rec.id ? "处理中..." : "接受"}
                </button>
                <button
                  onClick={() => handleReject(rec.id)}
                  disabled={operatingId === rec.id}
                  className="px-2 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600 disabled:opacity-50"
                >
                  {operatingId === rec.id ? "处理中..." : "拒绝"}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
