export interface Message {
  id: string;
  direction: string;
  content: string;
  sender: string;
  create_time: string;
}

export interface Conversation {
  id: string;
  conversation_pk?: number;
  platform: string;
  customer_id?: string;
  customer_pk?: number;
  customer_nick: string;
  status: string;
  assigned_agent: string | null;
}

export interface OrderItem {
  sku_id: string;
  sku_name: string;
  quantity: number;
  price: number;
  sub_total: number;
}

export interface Order {
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

export interface ShipmentTrace {
  time: string;
  message: string;
  location: string;
}

export interface ShipmentEntry {
  shipment_id: string;
  express_company: string;
  express_no: string;
  status: string;
  status_name: string;
  create_time: string | null;
  estimated_arrival: string | null;
  trace: ShipmentTrace[];
}

export interface Shipment {
  order_id: string;
  shipments: ShipmentEntry[];
}

export interface AfterSale {
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

export interface InventoryItem {
  sku_id: string;
  product_id: string;
  product_name: string;
  stock_state: string;
  quantity: number;
  warehouse_name: string;
}

export interface Inventory {
  order_id: string;
  items: InventoryItem[];
}

export interface ContextOrder {
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

export interface ConversationContext {
  conversation_id: number;
  orders: ContextOrder[];
}

export interface AISuggestion {
  intent: string;
  confidence: number;
  suggested_reply: string;
  used_tools: string[];
  risk_level: string;
  needs_human_review: boolean;
  source_summary?: string | null;
}
