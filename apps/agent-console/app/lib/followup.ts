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

export interface FollowUpTask {
  id: number;
  conversation_id: number | null;
  customer_id: number;
  order_id: string | null;
  task_type: string;
  trigger_source: string;
  title: string;
  description: string | null;
  suggested_copy: string | null;
  status: string;
  priority: string;
  due_date: string | null;
  completed_at: string | null;
  completed_by: string | null;
  extra_json: Record<string, unknown> | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface FollowUpTaskListResponse {
  items: FollowUpTask[];
  total: number;
  page: number;
  size: number;
}

export async function getFollowupTasksByConversationId(
  conversationId: number
): Promise<FollowUpTask[]> {
  const response = await fetchAPI<FollowUpTaskListResponse>(
    `/api/follow-up/tasks?conversation_id=${conversationId}`
  );
  return response?.items || [];
}

export async function getAllFollowupTasks(
  page: number = 1,
  size: number = 20
): Promise<FollowUpTaskListResponse> {
  return fetchAPI<FollowUpTaskListResponse>(
    `/api/follow-up/tasks?page=${page}&size=${size}`
  );
}

export async function executeFollowupTask(
  taskId: number,
  completedBy: string = DEFAULT_AGENT_ID
): Promise<FollowUpTask> {
  return fetchAPI<FollowUpTask>(`/api/follow-up/tasks/${taskId}/execute`, {
    method: "POST",
    body: JSON.stringify({ completed_by: completedBy }),
  });
}

export async function closeFollowupTask(
  taskId: number,
  completedBy: string = DEFAULT_AGENT_ID
): Promise<FollowUpTask> {
  return fetchAPI<FollowUpTask>(`/api/follow-up/tasks/${taskId}/close`, {
    method: "POST",
    body: JSON.stringify({ completed_by: completedBy }),
  });
}

const taskTypeLabels: Record<string, string> = {
  "consultation_no_order": "咨询未下单",
  "unpaid": "待付款",
  "shipment_exception": "物流异常",
  "after_sale_care": "售后跟进",
  "shipment_pending_timeout": "待发货超时",
  "after_sale_processing_timeout": "售后处理超时",
  manual: "手动创建",
};

const statusLabels: Record<string, string> = {
  pending: "待处理",
  completed: "已完成",
  closed: "已关闭",
};

export function getTaskTypeLabel(taskType: string): string {
  return taskTypeLabels[taskType] || taskType;
}

export function getStatusLabel(status: string): string {
  return statusLabels[status] || status;
}

export interface AutoEvaluateResponse {
  created_tasks: FollowUpTask[];
  skipped: number;
}

export async function autoEvaluateFollowup(
  conversationId: string,
  customerId: number,
): Promise<AutoEvaluateResponse> {
  return fetchAPI<AutoEvaluateResponse>(`/api/follow-up/auto-evaluate`, {
    method: "POST",
    body: JSON.stringify({
      conversation_id: conversationId,
      customer_id: customerId,
    }),
  });
}
