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

export interface RiskFlag {
  id: number;
  customer_id: number;
  conversation_id: number | null;
  risk_type: string;
  risk_level: string;
  description: string | null;
  extra_json: Record<string, unknown> | null;
  status: string;
  created_at: string | null;
  updated_at: string | null;
}

export async function getRiskFlagsByCustomerId(customerId: number): Promise<RiskFlag[]> {
  return fetchAPI<RiskFlag[]>(`/api/risk-flags?customer_id=${customerId}`);
}

export async function createRiskFlag(data: {
  customer_id: number;
  conversation_id?: number;
  risk_type: string;
  risk_level?: string;
  description?: string;
}): Promise<RiskFlag> {
  return fetchAPI<RiskFlag>("/api/risk-flags", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function resolveRiskFlag(riskFlagId: number): Promise<RiskFlag> {
  return fetchAPI<RiskFlag>(`/api/risk-flags/${riskFlagId}/resolve`, {
    method: "POST",
  });
}

export async function dismissRiskFlag(riskFlagId: number): Promise<RiskFlag> {
  return fetchAPI<RiskFlag>(`/api/risk-flags/${riskFlagId}/dismiss`, {
    method: "POST",
  });
}

export function extractCustomerIdNumber(customerIdString: string): number | null {
  const match = customerIdString.match(/\d+/);
  if (match) {
    return parseInt(match[0], 10);
  }
  return null;
}

const riskTypeLabels: Record<string, string> = {
  negative_sentiment: "负面情绪",
  complaint_tendency: "投诉倾向",
};

const riskLevelLabels: Record<string, string> = {
  low: "低风险",
  medium: "中风险",
  high: "高风险",
};

const statusLabels: Record<string, string> = {
  active: "待处理",
  resolved: "已处理",
  dismissed: "已忽略",
};

export function getRiskTypeLabel(riskType: string): string {
  return riskTypeLabels[riskType] || riskType;
}

export function getRiskLevelLabel(riskLevel: string): string {
  return riskLevelLabels[riskLevel] || riskLevel;
}

export function getStatusLabel(status: string): string {
  return statusLabels[status] || status;
}
