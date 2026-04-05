"use client";

import { useState, useEffect } from "react";
import {
  QualityInspectionResult,
  getQualityResultsByConversationId,
  getRuleTypeLabel,
  getSeverityLabel,
} from "../../../lib/quality";

interface QualityInspectionPanelProps {
  conversationPk: number;
}

const severityColors: Record<string, string> = {
  low: "bg-blue-100 text-blue-800",
  medium: "bg-yellow-100 text-yellow-800",
  high: "bg-red-100 text-red-800",
};

export default function QualityInspectionPanel({ conversationPk }: QualityInspectionPanelProps) {
  const [results, setResults] = useState<QualityInspectionResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchResults();
  }, [conversationPk]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getQualityResultsByConversationId(conversationPk);
      setResults(Array.isArray(data) ? data : []);
    } catch (err) {
      setError("质检结果加载失败");
      console.error("Failed to fetch quality results:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">质检结果</h3>
        <p className="text-sm text-gray-500">加载中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">质检结果</h3>
        <p className="text-sm text-red-500">{error}</p>
      </div>
    );
  }

  const hitResults = results.filter((r) => r.hit);

  if (hitResults.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="font-medium text-lg mb-3">质检结果</h3>
        <p className="text-sm text-green-600">未发现质检问题</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">质检结果 ({hitResults.length})</h3>
      <div className="space-y-3">
        {hitResults.map((result) => {
          const rule = result.evidence_json?.rule as string | undefined;
          const missing = result.evidence_json?.missing_facts as string[] | undefined;
          const conflicts = result.evidence_json?.conflicts as Array<{product_name: string; issue: string}> | undefined;
          return (
          <div key={result.id} className="border rounded p-3 text-sm">
            <div className="flex justify-between items-start mb-2">
              <div>
                <span className="font-medium">
                  {rule ? getRuleTypeLabel(rule) : `质检项 #${result.id}`}
                </span>
              </div>
              <span
                className={`px-2 py-0.5 text-xs rounded ${
                  severityColors[result.severity] || "bg-gray-100"
                }`}
              >
                {getSeverityLabel(result.severity)}
              </span>
            </div>
            {missing && missing.length > 0 && (
              <p className="text-gray-600 mb-2">缺失项：{missing.join("、")}</p>
            )}
            {conflicts && conflicts.length > 0 && (
              <div className="mb-2">
                {conflicts.map((c, i) => (
                  <p key={i} className="text-gray-600">
                    {c.product_name}：{c.issue}
                  </p>
                ))}
              </div>
            )}
            {result.created_at && (
              <p className="text-xs text-gray-500">
                检测于: {new Date(result.created_at).toLocaleString("zh-CN")}
              </p>
            )}
          </div>
          );
        })}
      </div>
    </div>
  );
}
