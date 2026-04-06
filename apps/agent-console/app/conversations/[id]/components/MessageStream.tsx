import type { Message } from "../types";

export default function MessageStream({ messages, waiting }: { messages: Message[]; waiting?: boolean }) {
  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`flex ${msg.direction === "inbound" ? "justify-start" : "justify-end"}`}
        >
          <div
            className={`max-w-md px-4 py-2 rounded-lg ${
              msg.direction === "inbound"
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
      {waiting && (
        <div className="flex justify-start">
          <div className="max-w-md px-4 py-2 rounded-lg bg-gray-50 text-gray-400 italic text-sm">
            等待客户回复…
          </div>
        </div>
      )}
    </div>
  );
}
