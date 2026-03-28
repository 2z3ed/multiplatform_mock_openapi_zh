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
    if (response.status === 404) {
      return null as T;
    }
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export interface CustomerProfile {
  id: number;
  customer_id: number;
  total_orders: number;
  total_spent: string;
  avg_order_value: string;
  extra_json: Record<string, unknown> | null;
  created_at: string | null;
  updated_at: string | null;
}

export async function getCustomerProfile(customerId: number): Promise<CustomerProfile | null> {
  return fetchAPI<CustomerProfile | null>(`/api/customers/${customerId}/profile`);
}
