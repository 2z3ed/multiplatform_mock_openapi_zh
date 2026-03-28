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

export interface CustomerTag {
  id: number;
  customer_id: number;
  tag_type: string;
  tag_value: string;
  source: string;
  extra_json: Record<string, unknown> | null;
  created_at: string | null;
  updated_at: string | null;
}

export async function getCustomerTags(customerId: number): Promise<CustomerTag[]> {
  return fetchAPI<CustomerTag[]>(`/api/customers/${customerId}/tags`);
}

export async function createCustomerTag(data: {
  customer_id: number;
  tag_type: string;
  tag_value: string;
}): Promise<CustomerTag> {
  return fetchAPI<CustomerTag>("/api/tags", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteCustomerTag(tagId: number): Promise<{ success: boolean }> {
  return fetchAPI<{ success: boolean }>(`/api/tags/${tagId}`, {
    method: "DELETE",
  });
}
