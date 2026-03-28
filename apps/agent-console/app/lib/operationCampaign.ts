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

export interface OperationCampaign {
  id: number;
  name: string;
  campaign_type: string;
  target_description: string | null;
  audience_json: Record<string, unknown> | null;
  preview_text: string | null;
  status: string;
  extra_json: Record<string, unknown> | null;
  created_at: string | null;
  updated_at: string | null;
}

export async function getAllCampaigns(): Promise<OperationCampaign[]> {
  return fetchAPI<OperationCampaign[]>("/api/operation-campaigns");
}

const statusLabels: Record<string, string> = {
  draft: "草稿",
  ready: "就绪",
  completed: "已完成",
  cancelled: "已取消",
};

export function getStatusLabel(status: string): string {
  return statusLabels[status] || status;
}

const campaignTypeLabels: Record<string, string> = {
  sms: "短信",
  push: "推送",
  email: "邮件",
  wecom: "企业微信",
};

export function getCampaignTypeLabel(campaignType: string): string {
  return campaignTypeLabels[campaignType] || campaignType;
}
