const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

type RequestOptions = RequestInit & { retry?: boolean };

export type LoginResponse = {
  access: string;
  refresh: string;
};

export type Subscription = {
  id: number;
  plan: "free" | "pro";
  plan_label: string;
  status: "active" | "trialing" | "canceled";
  price: number;
  billing_cycle: string;
  trial_started_at: string | null;
  trial_ends_at: string | null;
  is_trial_active: boolean;
  cancel_at_period_end: boolean;
  current_period_start: string | null;
  current_period_end: string | null;
  manual_validation_note: string;
  features: string[];
  created_at: string;
  updated_at: string;
};

export type BillingPlan = {
  id: string;
  label: string;
  price: number;
  billing_cycle: string;
  trial_days?: number;
  features: string[];
};

export type HelpChatResponse = {
  answer: string;
  sources: Array<{
    type: string;
    label: string;
    text: string;
    url?: string;
    organization?: string;
    subtopic?: string;
    population?: string;
    condition?: string;
  }>;
  tool_calls: Array<{ name: string; status: string; detail: string }>;
  used_profile: boolean;
  used_latest_checkin: boolean;
  conversation?: ChatConversation;
  user_message?: ChatMessage;
  ai_response?: ChatMessage;
};

export type ChatMessage = {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  message_type: string;
  metadata: Record<string, unknown>;
  sources: HelpChatResponse["sources"];
  tool_calls: HelpChatResponse["tool_calls"];
  created_at: string;
};

export type ChatConversation = {
  id: string;
  title: string;
  intent: string;
  system_prompt?: string;
  total_tokens_used?: number;
  created_at: string;
  updated_at: string;
  messages?: ChatMessage[];
};

export type UserPreferences = {
  theme: "light" | "dark";
  measurement_system: "metric" | "imperial";
  push_enabled: boolean;
  reminder_time: string;
  weekly_email_enabled: boolean;
  two_factor_enabled: boolean;
  notification_settings?: {
    pushEnabled: boolean;
    reminderTime: string;
    weeklyEmailEnabled: boolean;
  };
};

export type SecurityStatus = {
  email: string;
  last_login: string | null;
  password_changed_at: string | null;
  two_factor_enabled: boolean;
  can_change_password: boolean;
  can_delete_account: boolean;
};

type SubscriptionActionResponse = {
  success: boolean;
  message: string;
  data: Subscription;
};

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

function flattenErrors(value: unknown, prefix = ""): string[] {
  if (!value) return [];
  if (Array.isArray(value)) {
    return value.flatMap((item) => flattenErrors(item, prefix));
  }
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>).flatMap(([key, nested]) => {
      const label = prefix ? `${prefix}.${key}` : key;
      const messages = flattenErrors(nested, label);
      return messages.length ? messages : [`${label}: ${String(nested)}`];
    });
  }
  return [prefix ? `${prefix}: ${String(value)}` : String(value)];
}

function errorMessage(data: unknown, status: number) {
  if (typeof data !== "object" || !data) return `Request failed (${status})`;
  const body = data as { detail?: unknown; error?: unknown; errors?: unknown; details?: unknown };
  const fieldErrors = flattenErrors(body.errors ?? body.details);
  if (fieldErrors.length) return fieldErrors.join("\n");
  if (body.detail) return String(body.detail);
  if (body.error) return String(body.error);
  return `Request failed (${status})`;
}

const nullableNumberFields = new Set([
  "blood_pressure_systolic",
  "blood_pressure_diastolic",
  "cholesterol",
  "daily_steps",
  "avg_heart_rate",
  "caloric_intake",
  "protein_intake",
  "carbohydrate_intake",
  "fat_intake",
  "current_weight",
  "sleep_hours",
  "resting_heart_rate",
  "available_minutes",
]);

function normalizePayload(payload: Record<string, unknown>) {
  return Object.fromEntries(
    Object.entries(payload)
      .filter(([key]) => !["id", "user", "bmi", "bmi_level", "blood_pressure", "created_at", "updated_at"].includes(key))
      .map(([key, value]) => [key, nullableNumberFields.has(key) && value === "" ? null : value]),
  );
}

export const tokenStore = {
  accessToken: "",
  get access() {
    return this.accessToken;
  },
  get refresh() {
    return "";
  },
  set(access: string) {
    this.accessToken = access;
    localStorage.removeItem("fitgenius.accessToken");
    localStorage.removeItem("fitgenius.refreshToken");
  },
  clear() {
    this.accessToken = "";
    localStorage.removeItem("fitgenius.accessToken");
    localStorage.removeItem("fitgenius.refreshToken");
  },
};

async function parseResponse(response: Response) {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function refreshAccessToken() {
  const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    tokenStore.clear();
    return false;
  }

  const data = await parseResponse(response) as Partial<LoginResponse>;
  if (!data?.access) return false;
  tokenStore.set(data.access);
  return true;
}

export async function apiFetch<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  const hasBody = options.body !== undefined;

  if (hasBody && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (tokenStore.access) {
    headers.set("Authorization", `Bearer ${tokenStore.access}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include",
    headers,
  });

  if (response.status === 401 && options.retry !== false && await refreshAccessToken()) {
    return apiFetch<T>(path, { ...options, retry: false });
  }

  const data = await parseResponse(response);

  if (!response.ok) {
    throw new ApiError(errorMessage(data, response.status), response.status, data);
  }

  return data as T;
}

export const api = {
  login: (email: string, password: string) => apiFetch<LoginResponse>("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  }),
  register: (payload: Record<string, unknown>) => apiFetch("/auth/register/", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
  me: () => apiFetch("/auth/profile/"),
  logout: () => apiFetch("/auth/logout/", { method: "POST" }),
  security: () => apiFetch<SecurityStatus>("/auth/security/"),
  twoFactorStatus: () => apiFetch<{ two_factor_enabled: boolean }>("/auth/2fa/status/"),
  enableTwoFactor: () => apiFetch<{ success: boolean; two_factor_enabled: boolean }>("/auth/2fa/enable/", { method: "POST" }),
  disableTwoFactor: () => apiFetch<{ success: boolean; two_factor_enabled: boolean }>("/auth/2fa/disable/", { method: "POST" }),
  deleteAccount: (confirm_email: string) => apiFetch("/auth/account/", {
    method: "DELETE",
    body: JSON.stringify({ confirm_email }),
  }),
  preferences: () => apiFetch<UserPreferences>("/user/preferences/"),
  savePreferences: (payload: Partial<UserPreferences>) => apiFetch<UserPreferences>("/user/preferences/", {
    method: "PATCH",
    body: JSON.stringify(payload),
  }),
  notificationPreferences: () => apiFetch<UserPreferences>("/notifications/preferences/"),
  profile: () => apiFetch("/profiles/"),
  profileOptions: () => apiFetch("/profiles/options/"),
  profileDefaults: () => apiFetch("/profiles/defaults/"),
  saveProfile: (payload: Record<string, unknown>) => apiFetch("/profiles/", {
    method: "POST",
    body: JSON.stringify(normalizePayload(payload)),
  }),
  latestCheckIn: () => apiFetch("/checkins/latest/"),
  checkInOptions: () => apiFetch("/checkins/options/"),
  checkInHistory: () => apiFetch("/checkins/history/"),
  saveCheckIn: (payload: Record<string, unknown>) => apiFetch("/checkins/", {
    method: "POST",
    body: JSON.stringify(normalizePayload(payload)),
  }),
  latestRecommendation: () => apiFetch("/recommendations/latest/"),
  recommendationHistory: () => apiFetch("/recommendations/history/"),
  generateRecommendation: () => apiFetch<{ success: boolean; data: unknown }>("/recommendations/generate/", {
    method: "POST",
    body: JSON.stringify({}),
  }),
  dashboardSummary: () => apiFetch("/dashboard/summary/"),
  analyticsSummary: () => apiFetch("/analytics/summary/"),
  subscription: () => apiFetch<Subscription>("/billing/subscription/"),
  billingPlans: () => apiFetch<{ plans: BillingPlan[] }>("/billing/plans/"),
  startProTrial: (note = "User started free Pro trial") => apiFetch<SubscriptionActionResponse>("/billing/start-pro-trial/", {
    method: "POST",
    body: JSON.stringify({ note }),
  }),
  cancelSubscription: (note = "User canceled Pro trial") => apiFetch<SubscriptionActionResponse>("/billing/cancel/", {
    method: "POST",
    body: JSON.stringify({ note }),
  }),
  helpChat: (payload: { message: string; document_text?: string }) => apiFetch<HelpChatResponse>("/chat/", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
  chatConversations: () => apiFetch<ChatConversation[]>("/chat/conversations/"),
  createChatConversation: (payload: Partial<ChatConversation> = {}) => apiFetch<ChatConversation>("/chat/conversations/", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
  chatConversation: (id: string) => apiFetch<ChatConversation>(`/chat/conversations/${id}/`),
  deleteChatConversation: (id: string) => apiFetch(`/chat/conversations/${id}/`, { method: "DELETE" }),
  sendChatMessage: (id: string, payload: { message: string; document_text?: string }) => apiFetch<HelpChatResponse>(`/chat/conversations/${id}/message/`, {
    method: "POST",
    body: JSON.stringify(payload),
  }),
};
