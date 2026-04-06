import type { AISuggestion, SuggestionStatus } from "../types";

export default function SuggestionPanel({
  suggestion,
  status,
  onApply,
  onGenerate,
}: {
  suggestion: AISuggestion | null;
  status: SuggestionStatus;
  onApply: (text: string) => void;
  onGenerate: () => void;
}) {
  if (status.type === "loading") {
    return (
      <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
        <h3 className="font-medium text-lg mb-3">AI 建议回复</h3>
        <div className="flex items-center gap-2 text-sm text-gray-500 py-4">
          <svg className="animate-spin h-4 w-4 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>正在生成建议…</span>
        </div>
      </div>
    );
  }

  if (status.type === "error") {
    return (
      <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
        <h3 className="font-medium text-lg mb-3">AI 建议回复</h3>
        {suggestion && (
          <div className="mb-3">
            <p className="text-xs text-gray-500 mb-1">上一版建议</p>
            <div className="bg-gray-50 p-2 rounded text-sm">{suggestion.suggested_reply}</div>
          </div>
        )}
        <p className="text-sm text-red-600 mb-3">{status.message}</p>
        <button
          onClick={onGenerate}
          className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600"
        >
          重试
        </button>
      </div>
    );
  }

  if (status.type === "empty") {
    return (
      <div className="bg-white rounded-lg shadow p-4 border-l-4 border-gray-300">
        <h3 className="font-medium text-lg mb-3">AI 建议回复</h3>
        <p className="text-sm text-gray-500 mb-3">暂无可用建议</p>
        <button
          onClick={onGenerate}
          className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
        >
          重新生成
        </button>
      </div>
    );
  }

  if (status.type === "degraded") {
    return (
      <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
        <h3 className="font-medium text-lg mb-3">AI 建议回复</h3>
        {status.reason && (
          <div className="bg-yellow-50 border border-yellow-200 p-2 rounded mb-3">
            <p className="text-xs text-yellow-700">建议质量可能受限：{status.reason}</p>
          </div>
        )}
        {suggestion && (
          <>
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
            </div>
            <div className="bg-gray-50 p-3 rounded mb-4">
              <p className="text-sm">{suggestion.suggested_reply}</p>
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
            </div>
          </>
        )}
      </div>
    );
  }

  if (status.type === "idle") {
    return (
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
  }

  // success
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
