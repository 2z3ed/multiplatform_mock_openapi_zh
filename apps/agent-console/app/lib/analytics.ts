async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(endpoint, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}`;
    try {
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        const error = await response.json();
        if (error.detail) {
          if (typeof error.detail === "string") {
            errorMessage = error.detail;
          } else if (Array.isArray(error.detail)) {
            errorMessage = error.detail.map((e: { msg?: string }) => e.msg || JSON.stringify(e)).join("; ");
          } else {
            errorMessage = JSON.stringify(error.detail);
          }
        } else if (error.error) {
          errorMessage = typeof error.error === "string" ? error.error : JSON.stringify(error.error);
        }
      } else {
        const text = await response.text();
        errorMessage = text || errorMessage;
      }
    } catch {
      errorMessage = `HTTP ${response.status}`;
    }
    throw new Error(errorMessage);
  }

  return response.json();
}

export interface AnalyticsSummary {
  id: number;
  stat_date: string;
  recommendation_created_count: number;
  recommendation_accepted_count: number;
  followup_executed_count: number;
  followup_closed_count: number;
  operation_campaign_completed_count: number;
  extra_json: Record<string, unknown> | null;
  created_at: string | null;
  updated_at: string | null;
}

function formatDate(date: Date): string {
  return date.toISOString().split("T")[0];
}

function getDefaultDateRange(): { start_date: string; end_date: string } {
  const end = new Date();
  const start = new Date();
  start.setDate(start.getDate() - 6);
  return {
    start_date: formatDate(start),
    end_date: formatDate(end),
  };
}

export async function getAnalyticsSummaries(
  startDate?: string,
  endDate?: string
): Promise<AnalyticsSummary[]> {
  const range = getDefaultDateRange();
  const start = startDate || range.start_date;
  const end = endDate || range.end_date;
  return fetchAPI<AnalyticsSummary[]>(
    `/api/analytics/summaries?start_date=${start}&end_date=${end}`
  );
}
