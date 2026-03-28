"use client";

import { useState, useEffect, use } from "react";
import { useParams } from "next/navigation";
import FollowupPanel from "./components/FollowupPanel";
import RecommendationPanel from "./components/RecommendationPanel";
import RiskFlagPanel from "./components/RiskFlagPanel";
import CustomerProfilePanel from "./components/CustomerProfilePanel";

interface Message {
  id: string;
  direction: string;
  content: string;
  sender: string;
  create_time: string;
}

interface Conversation {
  id: string;
  conversation_pk?: number;
  platform: string;
  customer_id?: string;
  customer_pk?: number;
  customer_nick: string;
  status: string;
  assigned_agent: string | null;
}

interface Order {
  order_id: string;
  status: string;
  status_name: string;
  create_time: string;
  payment_amount: number;
  receiver_name: string;
  receiver_phone: string;
  items: { sku_name: string; quantity: number }[];
}

interface Shipment {
  shipments: {
    express_company: string;
    express_no: string;
    status: string;
    status_name: string;
  }[];
}

interface AfterSale {
  after_sale_id: string;
  type: string;
  type_name: string;
  status: string;
  status_name: string;
  apply_amount: number;
}

interface AISuggestion {
  intent: string;
  confidence: number;
  suggested_reply: string;
  used_tools: string[];
  risk_level: string;
  needs_human_review: boolean;
}

const platformLabels: Record<string, string> = {
  jd: "京东",
  douyin_shop: "抖音",
  wecom_kf: "企微",
};

function ConversationHeader({ conversation }: { conversation: Conversation }) {
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

  useEffect(() => {
    setText(initialText || "");
  }, [initialText]);

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

function OrderPanel({ order }: { order: Order | null }) {
  if (!order) return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">订单信息</h3>
      <p className="text-sm text-gray-500">暂无订单信息</p>
    </div>
  );
  
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

function ShipmentPanel({ shipment }: { shipment: Shipment | null }) {
  if (!shipment || !shipment.shipments?.length) return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">物流信息</h3>
      <p className="text-sm text-gray-500">暂无物流信息</p>
    </div>
  );
  
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

function AfterSalePanel({ afterSale }: { afterSale: AfterSale | null }) {
  if (!afterSale) return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">售后信息</h3>
      <p className="text-sm text-gray-500">暂无售后信息</p>
    </div>
  );
  
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

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ConversationDetailPage({ params }: { params: { id: string } }) {
  const convId = params.id;
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [order, setOrder] = useState<Order | null>(null);
  const [shipment, setShipment] = useState<Shipment | null>(null);
  const [afterSale, setAfterSale] = useState<AfterSale | null>(null);
  const [suggestion, setSuggestion] = useState<AISuggestion | null>(null);
  const [replyText, setReplyText] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [convRes, msgRes] = await Promise.all([
          fetch(`/api/conversations/${convId}`),
          fetch(`/api/conversations/${convId}/messages`),
        ]);
        
        const convData = await convRes.json();
        const msgData = await msgRes.json();
        
        setConversation(convData);
        setMessages(msgData.items || []);
        
        if (convData.platform === "jd") {
          const [orderRes, shipmentRes] = await Promise.all([
            fetch(`/api/orders/jd/${convId}`),
            fetch(`${API_URL}/api/shipments/jd/${convId}`),
          ]);
          const orderData = await orderRes.json();
          const shipmentData = await shipmentRes.json();
          setOrder(orderData.items?.[0] || null);
          setShipment(shipmentData.shipments ? shipmentData : null);
        }
      } catch (error) {
        console.error("Failed to fetch conversation data:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [convId]);

  const handleSend = async (text: string) => {
    const newMsg: Message = {
      id: `msg_${Date.now()}`,
      direction: "outbound",
      content: text,
      sender: "agent",
      create_time: new Date().toISOString(),
    };
    setMessages([...messages, newMsg]);

    try {
      await fetch("/api/audit-logs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          action: "message_sent",
          actor_type: "agent",
          actor_id: "agent_001",
          target_type: "message",
          target_id: newMsg.id,
          detail: `Sent message in conversation: ${convId}`,
          detail_json: { conversation_id: convId, content: text },
        }),
      });
    } catch (error) {
      console.error("Failed to create audit log:", error);
    }
  };

  const handleApplySuggestion = (text: string) => {
    setReplyText(text);
  };

  const handleGenerateSuggestion = async () => {
    try {
      const lastMsg = messages.filter(m => m.direction === "inbound").pop();
      if (!lastMsg) return;
      
      const res = await fetch(`${API_URL}/api/ai/suggest-reply`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: convId,
          message: lastMsg.content,
          platform: conversation?.platform || "jd",
        }),
      });
      const data = await res.json();
      setSuggestion(data);
    } catch (error) {
      console.error("Failed to generate suggestion:", error);
    }
  };

  if (loading) return <div className="p-8 text-center">加载中...</div>;
  if (!conversation) return <div className="p-8 text-center">会话不存在</div>;

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <ConversationHeader conversation={conversation} />
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col">
          <MessageStream messages={messages} />
          <ReplyComposer onSend={handleSend} initialText={replyText} />
        </div>
        <div className="w-80 border-l bg-gray-100 p-4 space-y-4 overflow-y-auto">
          <OrderPanel order={order} />
          <ShipmentPanel shipment={shipment} />
          <AfterSalePanel afterSale={afterSale} />
          <SuggestionPanel
            suggestion={suggestion}
            onApply={handleApplySuggestion}
            onGenerate={handleGenerateSuggestion}
          />
          {conversation?.conversation_pk && (
            <FollowupPanel conversationPk={conversation.conversation_pk} />
          )}
          {conversation?.conversation_pk && (
            <RecommendationPanel conversationPk={conversation.conversation_pk} />
          )}
          {conversation?.customer_pk && (
            <RiskFlagPanel customerPk={conversation.customer_pk} conversationPk={conversation.conversation_pk} />
          )}
          {conversation?.customer_pk && (
            <CustomerProfilePanel customerPk={conversation.customer_pk} />
          )}
        </div>
      </div>
    </div>
  );
}