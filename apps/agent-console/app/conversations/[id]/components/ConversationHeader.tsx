import type { Conversation } from "../types";

const platformLabels: Record<string, string> = {
  jd: "京东",
  taobao: "淘宝",
  douyin_shop: "抖音",
  wecom_kf: "企微",
  kuaishou: "快手",
  xhs: "小红书",
};

export default function ConversationHeader({ conversation }: { conversation: Conversation }) {
  return (
    <div className="bg-white border-b px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-medium">会话 {conversation.id}</h2>
          <p className="text-sm text-gray-500">
            客户: {conversation.customer_nick} | 平台: {platformLabels[conversation.platform] || conversation.platform}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <span
            className={`px-3 py-1 rounded-full text-sm ${
              conversation.status === "active"
                ? "bg-green-100 text-green-800"
                : "bg-yellow-100 text-yellow-800"
            }`}
          >
            {conversation.status === "active" ? "进行中" : "等待中"}
          </span>
        </div>
      </div>
    </div>
  );
}
