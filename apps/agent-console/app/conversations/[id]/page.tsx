"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";

interface Message {
  id: string;
  direction: string;
  content: string;
  sender: string;
  create_time: string;
}

interface Conversation {
  id: string;
  platform: string;
  customer_nick: string;
  status: string;
  assigned_agent: string | null;
}

const mockMessages: Message[] = [
  {
    id: "msg_001",
    direction: "inbound",
    content: "你好，我想查询一下我的订单状态",
    sender: "customer",
    create_time: "2024-03-20T14:00:00Z",
  },
  {
    id: "msg_002",
    direction: "outbound",
    content: "您好，请问您的订单号是多少？",
    sender: "agent",
    create_time: "2024-03-20T14:05:00Z",
  },
  {
    id: "msg_003",
    direction: "inbound",
    content: "订单号是 JD20240315001",
    sender: "customer",
    create_time: "2024-03-20T14:10:00Z",
  },
];

const mockOrder = {
  order_id: "JD20240315001",
  status: "PAID",
  status_name: "已付款",
  create_time: "2024-03-15T10:30:00Z",
  payment_amount: 289.0,
  receiver_name: "张三",
  receiver_phone: "13800138001",
  items: [{ sku_name: "iPhone 15 Pro 256GB 钛金属", quantity: 1 }],
};

const mockShipment = {
  shipments: [
    {
      express_company: "京东快递",
      express_no: "JD1234567890",
      status: "IN_TRANSIT",
      status_name: "运输中",
    },
  ],
};

const mockAfterSale = {
  after_sale_id: "AS20240320001",
  type: "REFUND",
  type_name: "退款",
  status: "APPROVED",
  status_name: "已通过",
  apply_amount: 289.0,
};

const mockSuggestion = {
  intent: "order_query",
  confidence: 0.85,
  suggested_reply: "您的订单 JD20240315001 目前状态是已付款，商品已发货，物流正在运输中，预计明天送达。",
  used_tools: ["get_order"],
  risk_level: "low",
  needs_human_review: true,
};

function ConversationHeader({ conversation }: { conversation: Conversation }) {
  return (
    <div className="bg-white border-b px-6 py-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-medium">会话 {conversation.id}</h2>
          <p className="text-sm text-gray-500">
            客户: {conversation.customer_nick} | 平台: {conversation.platform}
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

function MessageStream({ messages }: { messages: Message[] }) {
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
    </div>
  );
}

function ReplyComposer({
  onSend,
  initialText,
}: {
  onSend: (text: string) => void;
  initialText?: string;
}) {
  const [text, setText] = useState(initialText || "");

  return (
    <div className="border-t p-4 bg-white">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="输入回复内容..."
        className="w-full border rounded-lg p-3 min-h-[100px]"
      />
      <div className="mt-2 flex justify-end">
        <button
          onClick={() => {
            if (text.trim()) {
              onSend(text);
              setText("");
            }
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          发送
        </button>
      </div>
    </div>
  );
}

function OrderPanel({ order }: { order: typeof mockOrder }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">订单信息</h3>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">订单号:</span>
          <span>{order.order_id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">状态:</span>
          <span>{order.status_name}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">金额:</span>
          <span>¥{order.payment_amount}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">收货人:</span>
          <span>{order.receiver_name}</span>
        </div>
        <div className="mt-3 pt-3 border-t">
          <p className="text-gray-500 mb-1">商品:</p>
          {order.items.map((item, idx) => (
            <p key={idx} className="text-sm">
              {item.sku_name} x{item.quantity}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}

function ShipmentPanel({ shipment }: { shipment: typeof mockShipment }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">物流信息</h3>
      {shipment.shipments.map((ship, idx) => (
        <div key={idx} className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-500">快递:</span>
            <span>{ship.express_company}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">单号:</span>
            <span>{ship.express_no}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">状态:</span>
            <span>{ship.status_name}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function AfterSalePanel({ afterSale }: { afterSale: typeof mockAfterSale }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">售后信息</h3>
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">售后单号:</span>
          <span>{afterSale.after_sale_id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">类型:</span>
          <span>{afterSale.type_name}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">状态:</span>
          <span>{afterSale.status_name}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">金额:</span>
          <span>¥{afterSale.apply_amount}</span>
        </div>
      </div>
    </div>
  );
}

function SuggestionPanel({
  suggestion,
  onApply,
}: {
  suggestion: typeof mockSuggestion;
  onApply: (text: string) => void;
}) {
  return (
    <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
      <h3 className="font-medium text-lg mb-3">AI 建议回复</h3>
      <div className="space-y-2 text-sm mb-4">
        <div className="flex justify-between">
          <span className="text-gray-500">意图:</span>
          <span>{suggestion.intent}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">置信度:</span>
          <span>{(suggestion.confidence * 100).toFixed(0)}%</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">风险:</span>
          <span
            className={`${
              suggestion.risk_level === "low"
                ? "text-green-600"
                : "text-yellow-600"
            }`}
          >
            {suggestion.risk_level}
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
        <span className="text-xs text-gray-500 self-center">
          需人工确认后发送
        </span>
      </div>
    </div>
  );
}

export default function ConversationDetailPage() {
  const params = useParams();
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [replyText, setReplyText] = useState("");

  useEffect(() => {
    const convId = params.id as string;
    setConversation({
      id: convId,
      platform: "jd",
      customer_nick: "用户_13800138000",
      status: "active",
      assigned_agent: "agent_001",
    });
    setMessages(mockMessages);
  }, [params.id]);

  const handleSend = (text: string) => {
    const newMsg: Message = {
      id: `msg_${Date.now()}`,
      direction: "outbound",
      content: text,
      sender: "agent",
      create_time: new Date().toISOString(),
    };
    setMessages([...messages, newMsg]);
  };

  const handleApplySuggestion = (text: string) => {
    setReplyText(text);
  };

  if (!conversation) return <div>加载中...</div>;

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <ConversationHeader conversation={conversation} />
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col">
          <MessageStream messages={messages} />
          <ReplyComposer onSend={handleSend} initialText={replyText} />
        </div>
        <div className="w-80 border-l bg-gray-100 p-4 space-y-4 overflow-y-auto">
          <OrderPanel order={mockOrder} />
          <ShipmentPanel shipment={mockShipment} />
          <AfterSalePanel afterSale={mockAfterSale} />
          <SuggestionPanel
            suggestion={mockSuggestion}
            onApply={handleApplySuggestion}
          />
        </div>
      </div>
    </div>
  );
}