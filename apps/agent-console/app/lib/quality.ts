const DEFAULT_AGENT_ID = "demo-agent";

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

export interface QualityInspectionResult {
  id: number;
  conversation_id: number;
  quality_rule_id: number;
  hit: boolean;
  severity: string;
  evidence_json: Record<string, unknown> | null;
  inspected_at: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface AutoEvaluateQualityResponse {
  created_results: QualityInspectionResult[];
  skipped: number;
}

export async function getQualityResultsByConversationId(
  conversationId: number
): Promise<QualityInspectionResult[]> {
  const response = await fetchAPI<QualityInspectionResult[]>(
    `/api/quality/results?conversation_id=${conversationId}`
  );
  return Array.isArray(response) ? response : [];
}

export async function autoEvaluateQuality(
  conversationId: string,
): Promise<AutoEvaluateQualityResponse> {
  return fetchAPI<AutoEvaluateQualityResponse>(`/api/quality/auto-evaluate`, {
    method: "POST",
    body: JSON.stringify({
      conversation_id: conversationId,
    }),
  });
}

const ruleTypeLabels: Record<string, string> = {
  slow_reply: "回复过慢",
  missed_response: "遗漏回复",
  forbidden_word: "禁用词",
  insufficient_explanation: "解释依据不足",
  incomplete_after_sale_reply: "售后答复不完整",
  inventory_reply_conflict: "库存答复冲突",
};

const severityLabels: Record<string, string> = {
  low: "提示",
  medium: "警告",
  high: "严重",
};

export function getRuleTypeLabel(ruleType: string): string {
  return ruleTypeLabels[ruleType] || ruleType;
}

export function getSeverityLabel(severity: string): string {
  return severityLabels[severity] || severity;
}
