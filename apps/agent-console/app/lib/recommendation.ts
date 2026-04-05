async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(endpoint, {
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

export interface Recommendation {
  id: number;
  conversation_id: number;
  customer_id: number;
  product_id: string;
  product_name: string;
  reason: string | null;
  suggested_copy: string | null;
  status: string;
  extra_json: Record<string, unknown> | null;
  created_at: string | null;
  updated_at: string | null;
}

export async function getRecommendationsByConversationId(
  conversationId: number
): Promise<Recommendation[]> {
  const response = await fetchAPI<Recommendation[]>(
    `/api/conversations/${conversationId}/recommendations`
  );
  return Array.isArray(response) ? response : [];
}

export async function acceptRecommendation(
  recommendationId: number
): Promise<Recommendation> {
  return fetchAPI<Recommendation>(`/api/recommendations/${recommendationId}/accept`, {
    method: "POST",
  });
}

export async function rejectRecommendation(
  recommendationId: number
): Promise<Recommendation> {
  return fetchAPI<Recommendation>(`/api/recommendations/${recommendationId}/reject`, {
    method: "POST",
  });
}

const statusLabels: Record<string, string> = {
  pending: "待处理",
  accepted: "已接受",
  rejected: "已拒绝",
};

export function getStatusLabel(status: string): string {
  return statusLabels[status] || status;
}

export interface AutoEvaluateRecommendationResponse {
  created_recommendations: Recommendation[];
  skipped: number;
}

export async function autoEvaluateRecommendation(
  conversationId: string,
  customerId: number,
): Promise<AutoEvaluateRecommendationResponse> {
  return fetchAPI<AutoEvaluateRecommendationResponse>(`/api/recommendations/auto-evaluate`, {
    method: "POST",
    body: JSON.stringify({
      conversation_id: conversationId,
      customer_id: customerId,
    }),
  });
}

const ruleLabels: Record<string, string> = {
  "inventory_shortage": "库存不足",
  "shipment_pending_timeout": "待发货超时",
  "after_sale_processing_timeout": "售后处理超时",
};

export function getRuleLabel(rule: string): string {
  return ruleLabels[rule] || rule;
}
