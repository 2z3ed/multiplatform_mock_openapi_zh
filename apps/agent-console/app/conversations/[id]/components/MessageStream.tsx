import type { Message } from "../types";

export default function MessageStream({
  messages,
  waiting,
  hasTimedOut,
  newMessageId,
}: {
  messages: Message[];
  waiting?: boolean;
  hasTimedOut?: boolean;
  newMessageId?: string | null;
}) {
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="text-center">
          <svg className="mx-auto w-12 h-12 text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p className="text-sm text-gray-400">暂无消息历史</p>
          <p className="text-xs text-gray-300 mt-1">发送第一条消息开始对话</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${msg.direction === "inbound" ? "justify-start" : "justify-end"}`}
        >
          <div
            className={`max-w-md px-4 py-2 rounded-lg transition-all duration-300 ${
              msg.id === newMessageId
                ? "bg-green-50 ring-2 ring-green-200 text-gray-800"
                : msg.direction === "inbound"
                ? "bg-gray-100 text-gray-800"
                : "bg-blue-500 text-white"
            }`}
          >
            <p className="text-sm">{msg.content}</p>
            <p className="text-xs mt-1 opacity-70">
              {new Date(msg.create_time).toLocaleString("zh-CN")}
            </p>
          </div>
        </div>
      ))}
      {waiting && !hasTimedOut && (
        <div className="flex justify-start">
          <div className="max-w-md px-4 py-2 rounded-lg bg-gray-50 text-gray-400 italic text-sm">
            等待客户回复…
          </div>
        </div>
      )}
      {hasTimedOut && !waiting && (
        <div className="flex justify-start">
          <div className="max-w-md px-4 py-2 rounded-lg bg-yellow-50 text-yellow-600 text-sm">
            客户暂未回复，您可以继续发送消息
          </div>
        </div>
      )}
    </div>
  );
}
