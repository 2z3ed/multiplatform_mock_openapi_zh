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

export interface PlatformAccount {
  id: string;
  platform: string;
  account_name: string;
  provider_mode: "mock" | "real";
  status: "active" | "inactive";
  last_sync: string;
}

export interface KBDocument {
  document_id: string;
  title: string;
  doc_type: string;
  chunk_count: number;
  created_at: string;
}

export interface AuditLog {
  id: string;
  action: string;
  user: string;
  resource: string;
  timestamp: string;
  details: string;
}

export async function getPlatformAccounts(): Promise<PlatformAccount[]> {
  return fetchAPI("/api/platforms");
}

export async function updateProviderMode(
  platformId: string,
  mode: "mock" | "real"
): Promise<{ status: string; provider_mode: string }> {
  return fetchAPI(`/api/platforms/${platformId}/mode`, {
    method: "PUT",
    body: JSON.stringify({ provider_mode: mode }),
  });
}

export async function getDocuments(): Promise<KBDocument[]> {
  return fetchAPI("/api/kb/documents");
}

export async function uploadDocument(data: {
  title: string;
  content: string;
  doc_type: string;
}): Promise<KBDocument> {
  return fetchAPI("/api/kb/documents", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function reindexDocuments(): Promise<{
  status: string;
  total_documents: number;
  total_chunks: number;
}> {
  return fetchAPI("/api/kb/reindex", { method: "POST" });
}

export async function getAuditLogs(params?: {
  action?: string;
  user?: string;
  start_time?: string;
  end_time?: string;
}): Promise<AuditLog[]> {
  const query = new URLSearchParams();
  if (params?.action) query.set("action", params.action);
  if (params?.user) query.set("user", params.user);
  if (params?.start_time) query.set("start_time", params.start_time);
  if (params?.end_time) query.set("end_time", params.end_time);
  return fetchAPI(`/api/audit-logs?${query}`);
}