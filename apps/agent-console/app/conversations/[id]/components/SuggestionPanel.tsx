import type { AISuggestion } from "../types";

export default function SuggestionPanel({
  suggestion,
  onApply,
  onGenerate,
}: {
  suggestion: AISuggestion | null;
  onApply: (text: string) => void;
  onGenerate: () => void;
}) {
  if (!suggestion) return (
    <div className="bg-white rounded-lg shadow p-4 border-l-4 border-gray-300">
      <h3 className="font-medium text-lg mb-3">AI 建议回复</h3>
      <button
        onClick={onGenerate}
        className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
      >
        生成建议
      </button>
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
      <h3 className="font-medium text-lg mb-3">AI 建议回复</h3>
      <div className="space-y-2 text-sm mb-4">
        <div className="flex justify-between">
          <span className="text-gray-500">意图:</span>
          <span>{suggestion.intent || "-"}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">置信度:</span>
          <span>
            {typeof suggestion.confidence === "number"
              ? `${(suggestion.confidence * 100).toFixed(0)}%`
              : "-"}
          </span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">风险:</span>
          <span
            className={`${
              suggestion.risk_level === "low"
                ? "text-green-600"
                : suggestion.risk_level === "high"
                ? "text-red-600"
                : "text-yellow-600"
            }`}
          >
            {suggestion.risk_level || "-"}
          </span>
        </div>
      </div>
      {suggestion.source_summary && (
        <div className="bg-amber-50 border border-amber-200 p-3 rounded mb-3">
          <p className="text-xs text-amber-700 font-medium mb-1">业务依据</p>
          <p className="text-xs text-amber-800">{suggestion.source_summary}</p>
        </div>
      )}
      <div className="bg-gray-50 p-3 rounded mb-4">
        <p className="text-sm">{suggestion.suggested_reply || "暂无建议内容"}</p>
      </div>
      <div className="flex gap-2">
        <button
          onClick={() => onApply(suggestion.suggested_reply)}
          className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
        >
          使用建议回复
        </button>
        <button
          onClick={onGenerate}
          className="px-3 py-1 bg-gray-500 text-white text-sm rounded hover:bg-gray-600"
        >
          重新生成
        </button>
        <span className="text-xs text-gray-500 self-center">
          需人工确认后发送
        </span>
      </div>
    </div>
  );
}
