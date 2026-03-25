const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export interface Conversation {
  id: string;
  platform: string;
  customer_id: string;
  customer_nick: string;
  status: string;
  assigned_agent: string | null;
  unread_count: number;
  last_message_time: string;
  created_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  direction: string;
  content: string;
  sender: string;
  create_time: string;
}

export interface Order {
  platform: string;
  order_id: string;
  status: string;
  status_name: string;
  create_time: string | null;
  pay_time: string | null;
  total_amount: number;
  freight_amount: number;
  discount_amount: number;
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
  items: Array<{
    sku_id: string;
    sku_name: string;
    quantity: number;
    price: number;
    sub_total: number;
  }>;
}

export interface Shipment {
  platform: string;
  order_id: string;
  shipments: Array<{
    shipment_id: string;
    express_company: string;
    express_no: string;
    status: string;
    status_name: string;
    create_time: string | null;
    estimated_arrival: string | null;
    trace: Array<{
      time: string;
      message: string;
      location: string;
    }>;
  }>;
}

export interface AfterSale {
  platform: string;
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

export interface AISuggestion {
  intent: string;
  confidence: number;
  suggested_reply: string;
  used_tools: string[];
  risk_level: string;
  needs_human_review: boolean;
}

export async function getConversations(params?: {
  platform?: string;
  status?: string;
  assigned_agent?: string;
  skip?: number;
  limit?: number;
}): Promise<{ total: number; items: Conversation[] }> {
  const query = new URLSearchParams();
  if (params?.platform) query.set("platform", params.platform);
  if (params?.status) query.set("status", params.status);
  if (params?.assigned_agent !== undefined) query.set("assigned_agent", params.assigned_agent);
  if (params?.skip) query.set("skip", String(params.skip));
  if (params?.limit) query.set("limit", String(params.limit));
  return fetchAPI(`/api/conversations?${query}`);
}

export async function getConversation(id: string): Promise<Conversation> {
  return fetchAPI(`/api/conversations/${id}`);
}

export async function getMessages(
  conversationId: string,
  params?: { skip?: number; limit?: number }
): Promise<{ total: number; items: Message[] }> {
  const query = new URLSearchParams();
  if (params?.skip) query.set("skip", String(params.skip));
  if (params?.limit) query.set("limit", String(params.limit));
  return fetchAPI(`/api/conversations/${conversationId}/messages?${query}`);
}

export async function assignConversation(conversationId: string, agentId: string): Promise<{ status: string; conversation_id: string; assigned_agent: string }> {
  return fetchAPI(`/api/conversations/${conversationId}/assign`, {
    method: "POST",
    body: JSON.stringify({ agent_id: agentId }),
  });
}

export async function handoffConversation(conversationId: string, targetAgent: string): Promise<{ status: string; conversation_id: string; handoff_to: string }> {
  return fetchAPI(`/api/conversations/${conversationId}/handoff`, {
    method: "POST",
    body: JSON.stringify({ target_agent: targetAgent }),
  });
}

export async function getOrder(platform: string, orderId: string): Promise<Order> {
  return fetchAPI(`/api/orders/${platform}/${orderId}`);
}

export async function getShipment(platform: string, orderId: string): Promise<Shipment> {
  return fetchAPI(`/api/shipments/${platform}/${orderId}`);
}

export async function getAfterSale(platform: string, afterSaleId: string): Promise<AfterSale> {
  return fetchAPI(`/api/after-sales/${platform}/${afterSaleId}`);
}

export async function suggestReply(data: {
  conversation_id: string;
  message: string;
  platform?: string;
  order_id?: string;
}): Promise<AISuggestion> {
  return fetchAPI("/api/ai/suggest-reply", {
    method: "POST",
    body: JSON.stringify(data),
  });
}