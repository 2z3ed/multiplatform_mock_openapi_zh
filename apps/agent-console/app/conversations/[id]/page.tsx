"use client";

import { useState, useEffect, useRef } from "react";
import { useParams } from "next/navigation";
import FollowupPanel from "./components/FollowupPanel";
import RecommendationPanel from "./components/RecommendationPanel";
import RiskFlagPanel from "./components/RiskFlagPanel";
import CustomerProfilePanel from "./components/CustomerProfilePanel";
import QualityInspectionPanel from "./components/QualityInspectionPanel";
import { autoEvaluateFollowup } from "../../lib/followup";
import { autoEvaluateRecommendation } from "../../lib/recommendation";
import { autoEvaluateRisk } from "../../lib/riskFlag";
import { autoEvaluateQuality } from "../../lib/quality";

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

interface OrderItem {
  sku_id: string;
  sku_name: string;
  quantity: number;
  price: number;
  sub_total: number;
}

interface Order {
  order_id: string;
  status: string;
  status_name: string;
  create_time: string | null;
  pay_time: string | null;
  total_amount: number;
  payment_amount: number;
  buyer_nick: string | null;
  buyer_phone: string | null;
  receiver_name: string | null;
  receiver_phone: string | null;
  receiver_address: {
    province: string;
    city: string;
    district: string;
    detail: string;
  } | null;
  items: OrderItem[];
}

interface ShipmentTrace {
  time: string;
  message: string;
  location: string;
}

interface ShipmentEntry {
  shipment_id: string;
  express_company: string;
  express_no: string;
  status: string;
  status_name: string;
  create_time: string | null;
  estimated_arrival: string | null;
  trace: ShipmentTrace[];
}

interface Shipment {
  order_id: string;
  shipments: ShipmentEntry[];
}

interface AfterSale {
  after_sale_id: string;
  order_id: string;
  type: string;
  type_name: string;
  status: string;
  status_name: string;
  apply_time: string | null;
  handle_time: string | null;
  apply_amount: number;
  approve_amount: number;
  reason: string | null;
  reason_detail: string | null;
}

interface InventoryItem {
  sku_id: string;
  product_id: string;
  product_name: string;
  stock_state: string;
  quantity: number;
  warehouse_name: string;
}

interface Inventory {
  order_id: string;
  items: InventoryItem[];
}

interface ContextOrder {
  internal_order_id: number;
  link_type: string;
  platform: string | null;
  external_order_id: string | null;
  order_core_status: string | null;
  order: Order | null;
  shipment: Shipment | null;
  after_sales: AfterSale[];
  inventory: Inventory | null;
}

interface ConversationContext {
  conversation_id: number;
  orders: ContextOrder[];
}

interface AISuggestion {
  intent: string;
  confidence: number;
  suggested_reply: string;
  used_tools: string[];
  risk_level: string;
  needs_human_review: boolean;
  source_summary?: string | null;
}

const platformLabels: Record<string, string> = {
  jd: "京东",
  taobao: "淘宝",
  douyin_shop: "抖音",
  wecom_kf: "企微",
  kuaishou: "快手",
  xhs: "小红书",
};

const stockStateLabels: Record<string, string> = {
  in_stock: "有货",
  low_stock: "低库存",
  out_of_stock: "缺货",
  pre_order: "预售",
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

function OrderPanel({ order, platform }: { order: Order | null; platform?: string }) {
  if (!order) return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">订单信息</h3>
      <p className="text-sm text-gray-500">
        {platform === "wecom_kf" ? "当前平台暂不支持订单上下文" : "暂无订单信息"}
      </p>
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
          <span>{order.receiver_name || "-"}</span>
        </div>
        {order.receiver_address?.city && (
          <div className="flex justify-between">
            <span className="text-gray-500">收货地:</span>
            <span>{order.receiver_address.city}{order.receiver_address.district || ""}</span>
          </div>
        )}
        <div className="mt-3 pt-3 border-t">
          <p className="text-gray-500 mb-1">商品:</p>
          {(order.items || []).map((item, idx) => (
            <p key={idx} className="text-sm">
              {item.sku_name} x{item.quantity}
            </p>
          ))}
        </div>
      </div>
    </div>
  );
}

function ShipmentPanel({ shipment, platform }: { shipment: Shipment | null; platform?: string }) {
  if (!shipment || !shipment.shipments?.length) return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">物流信息</h3>
      <p className="text-sm text-gray-500">
        {platform === "wecom_kf" ? "当前平台暂不支持物流信息" : platform === "douyin_shop" ? "当前平台暂不支持物流查询" : "暂无物流信息"}
      </p>
    </div>
  );
  
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">物流信息</h3>
      {shipment.shipments.map((ship, idx) => (
        <div key={idx} className="space-y-2 text-sm mb-3 last:mb-0">
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
          {ship.trace.length > 0 && (
            <div className="mt-2 pt-2 border-t">
              <p className="text-gray-500 mb-1">最新物流:</p>
              <p className="text-xs text-gray-600">
                {ship.trace[0].message}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {ship.trace[0].time ? new Date(ship.trace[0].time).toLocaleString("zh-CN") : ""}
              </p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function AfterSalePanel({ afterSales, platform }: { afterSales: AfterSale[]; platform?: string }) {
  if (!afterSales || afterSales.length === 0) return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">售后信息</h3>
      <p className="text-sm text-gray-500">
        {platform === "wecom_kf" ? "当前平台暂不支持售后信息" : "暂无售后信息"}
      </p>
    </div>
  );
  
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">售后信息 ({afterSales.length})</h3>
      {afterSales.map((as, idx) => (
        <div key={idx} className="space-y-2 text-sm mb-3 last:mb-0">
          <div className="flex justify-between">
            <span className="text-gray-500">售后单号:</span>
            <span>{as.after_sale_id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">类型:</span>
            <span>{as.type_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">状态:</span>
            <span>{as.status_name}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-500">金额:</span>
            <span>¥{as.apply_amount}</span>
          </div>
          {as.reason && (
            <div className="mt-2 pt-2 border-t">
              <p className="text-gray-500 mb-1">原因:</p>
              <p className="text-xs text-gray-600">{as.reason}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function InventoryPanel({ inventory, platform }: { inventory: Inventory | null; platform?: string }) {
  const [expanded, setExpanded] = useState(false);

  if (!inventory || !inventory.items?.length) return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">库存信息</h3>
      <p className="text-sm text-gray-500">
        {platform === "wecom_kf" ? "当前平台暂不支持库存信息" : "暂无库存信息"}
      </p>
    </div>
  );

  const items = inventory.items;
  const outOfStock = items.filter(i => i.stock_state === "out_of_stock");
  const lowStock = items.filter(i => i.stock_state === "low_stock");
  const inStock = items.filter(i => i.stock_state === "in_stock");

  let overallLabel = "库存充足";
  let overallColor = "text-green-600";
  if (outOfStock.length > 0) {
    overallLabel = "存在缺货风险";
    overallColor = "text-red-600";
  } else if (lowStock.length > 0) {
    overallLabel = "存在低库存";
    overallColor = "text-yellow-600";
  }

  // Sort: out_of_stock first, then low_stock, then in_stock
  const sorted = [...items].sort((a, b) => {
    const order = { out_of_stock: 0, low_stock: 1, in_stock: 2 };
    return (order[a.stock_state as keyof typeof order] ?? 3) - (order[b.stock_state as keyof typeof order] ?? 3);
  });

  const displayItems = expanded ? sorted : sorted.slice(0, 5);

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="font-medium text-lg mb-3">库存信息</h3>
      {/* Summary */}
      <div className="mb-3 p-2 bg-gray-50 rounded text-xs">
        <div className="flex justify-between items-center">
          <span className="text-gray-500">SKU 总数: {items.length}</span>
          <span className={`font-medium ${overallColor}`}>{overallLabel}</span>
        </div>
        <div className="flex gap-3 mt-1 text-gray-400">
          <span>有货 {inStock.length}</span>
          <span>低库存 {lowStock.length}</span>
          <span>缺货 {outOfStock.length}</span>
        </div>
      </div>
      {/* Items */}
      {displayItems.map((item, idx) => (
        <div key={idx} className="flex items-center justify-between py-1.5 text-xs border-b last:border-0">
          <div className="flex-1 min-w-0">
            <span className="font-medium truncate block">{item.product_name || item.sku_id}</span>
            {item.warehouse_name && (
              <span className="text-gray-400">{item.warehouse_name}</span>
            )}
          </div>
          <div className="flex items-center gap-2 ml-2 shrink-0">
            <span className={`px-1.5 py-0.5 rounded text-xs ${
              item.stock_state === "out_of_stock" ? "bg-red-100 text-red-700" :
              item.stock_state === "low_stock" ? "bg-yellow-100 text-yellow-700" :
              "bg-green-100 text-green-700"
            }`}>
              {stockStateLabels[item.stock_state] || item.stock_state}
            </span>
            <span className="text-gray-500 w-8 text-right">{item.quantity}</span>
          </div>
        </div>
      ))}
      {/* Expand/Collapse */}
      {items.length > 5 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full mt-2 text-xs text-blue-600 hover:text-blue-800 py-1"
        >
          {expanded ? `收起` : `查看全部 ${items.length} 个 SKU`}
        </button>
      )}
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

export default function ConversationDetailPage() {
  const params = useParams();
  const convId = params.id as string;
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [context, setContext] = useState<ConversationContext | null>(null);
  const [suggestion, setSuggestion] = useState<AISuggestion | null>(null);
  const [replyText, setReplyText] = useState("");
  const [customerReplyText, setCustomerReplyText] = useState("");
  const [loading, setLoading] = useState(true);
  const evaluatedRef = useRef(false);

  useEffect(() => {
    if (evaluatedRef.current) return;
    evaluatedRef.current = true;

    async function fetchData() {
      try {
        const [convRes, msgRes, ctxRes] = await Promise.all([
          fetch(`/api/conversations/${convId}`),
          fetch(`/api/conversations/${convId}/messages`),
          fetch(`/api/conversations/${convId}/context`),
        ]);
        
        const convData = await convRes.json();
        const msgData = await msgRes.json();
        
        setConversation(convData);
        setMessages(msgData.items || []);
        
        if (ctxRes.ok) {
          const ctxData = await ctxRes.json();
          setContext(ctxData);
        } else {
          setContext(null);
        }
      } catch (error) {
        console.error("Failed to fetch conversation data:", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [convId]);

  useEffect(() => {
    if (!context || !conversation) return;

    const customerId = conversation.customer_pk;
    const convIdStr = String(conversation.conversation_pk || convId);

    async function runAutoEvaluations() {
      const evaluations = [];

      if (customerId) {
        evaluations.push(
          autoEvaluateFollowup(convIdStr, customerId).catch((e) => console.warn("Auto-evaluate followup failed:", e)),
          autoEvaluateRecommendation(convIdStr, customerId).catch((e) => console.warn("Auto-evaluate recommendation failed:", e)),
          autoEvaluateRisk(convIdStr, customerId).catch((e) => console.warn("Auto-evaluate risk failed:", e)),
        );
      }

      evaluations.push(
        autoEvaluateQuality(convIdStr).catch((e) => console.warn("Auto-evaluate quality failed:", e)),
      );

      await Promise.allSettled(evaluations);
    }

    runAutoEvaluations();
  }, [context, conversation, convId]);

  const handleSend = async (text: string) => {
    try {
      const response = await fetch(`/api/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: convId,
          content: text,
          sender_type: "agent",
          sender_id: "agent_001",
        }),
      });

      if (response.ok) {
        const fetchMsgs = await fetch(`/api/conversations/${convId}/messages`);
        if (fetchMsgs.ok) {
          const msgData = await fetchMsgs.json();
          setMessages(msgData.items || []);
        }
      }
    } catch (error) {
      console.error("Failed to send message:", error);
    }
  };

  const handleCustomerSend = async (text: string) => {
    try {
      const response = await fetch(`/api/messages/inbound`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          conversation_id: convId,
          content: text,
        }),
      });

      if (response.ok) {
        const fetchMsgs = await fetch(`/api/conversations/${convId}/messages`);
        if (fetchMsgs.ok) {
          const msgData = await fetchMsgs.json();
          setMessages(msgData.items || []);
        }
        setCustomerReplyText("");
      }
    } catch (error) {
      console.error("Failed to send customer message:", error);
    }
  };

  const handleApplySuggestion = (text: string) => {
    setReplyText(text);
  };

  const handleGenerateSuggestion = async () => {
    try {
      const lastMsg = messages.filter(m => m.direction === "inbound").pop();
      if (!lastMsg) return;
      
      const res = await fetch(`/api/ai/suggest-reply`, {
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

  const firstOrder = context?.orders?.[0] || null;
  const orderData = firstOrder?.order || null;
  const shipmentData = firstOrder?.shipment || null;
  const afterSalesData = firstOrder?.after_sales || [];
  const inventoryData = firstOrder?.inventory || null;
  const platform = firstOrder?.platform || conversation.platform;

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <ConversationHeader conversation={conversation} />
      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col">
          <MessageStream messages={messages} />
          <ReplyComposer onSend={handleSend} initialText={replyText} />
          <div className="border-t bg-yellow-50 p-3">
            <p className="text-xs text-yellow-700 mb-2">🔧 开发态：模拟客户回复</p>
            <div className="flex gap-2">
              <input
                className="flex-1 border rounded px-3 py-2 text-sm"
                placeholder="输入客户回复内容..."
                value={customerReplyText}
                onChange={(e) => setCustomerReplyText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && customerReplyText.trim()) {
                    handleCustomerSend(customerReplyText.trim());
                  }
                }}
              />
              <button
                onClick={() => {
                  if (customerReplyText.trim()) {
                    handleCustomerSend(customerReplyText.trim());
                  }
                }}
                className="px-3 py-2 bg-yellow-600 text-white text-sm rounded hover:bg-yellow-700"
              >
                发送
              </button>
            </div>
          </div>
        </div>
        <div className="w-80 border-l bg-gray-100 p-4 space-y-4 overflow-y-auto">
          <OrderPanel order={orderData} platform={platform} />
          <ShipmentPanel shipment={shipmentData} platform={platform} />
          <AfterSalePanel afterSales={afterSalesData} platform={platform} />
          <InventoryPanel inventory={inventoryData} platform={platform} />
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
          {conversation?.conversation_pk && (
            <QualityInspectionPanel conversationPk={conversation.conversation_pk} />
          )}
        </div>
      </div>
    </div>
  );
}
