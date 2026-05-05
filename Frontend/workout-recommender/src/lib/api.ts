const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

type RequestOptions = RequestInit & { retry?: boolean };

export type LoginResponse = {
  access: string;
  refresh: string;
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

export const tokenStore = {
  get access() {
    return localStorage.getItem("fitgenius.accessToken");
  },
  get refresh() {
    return localStorage.getItem("fitgenius.refreshToken");
  },
  set(access: string, refresh?: string) {
    localStorage.setItem("fitgenius.accessToken", access);
    if (refresh) localStorage.setItem("fitgenius.refreshToken", refresh);
  },
  clear() {
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
  const refresh = tokenStore.refresh;
  if (!refresh) return false;

  const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    tokenStore.clear();
    return false;
  }

  const data = await parseResponse(response) as Partial<LoginResponse>;
  if (!data?.access) return false;
  tokenStore.set(data.access, data.refresh);
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
    const message = typeof data === "object" && data && "detail" in data ? String((data as { detail: unknown }).detail) : `Request failed (${response.status})`;
    throw new ApiError(message, response.status, data);
  }

  return data as T;
}

export const api = {
  login: (username: string, password: string) => apiFetch<LoginResponse>("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  }),
  register: (payload: Record<string, unknown>) => apiFetch("/auth/register/", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
  me: () => apiFetch("/auth/profile/"),
  logout: () => apiFetch("/auth/logout/", { method: "POST" }),
  profile: () => apiFetch("/profiles/"),
  saveProfile: (payload: Record<string, unknown>) => apiFetch("/profiles/", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
  latestCheckIn: () => apiFetch("/checkins/latest/"),
  checkInHistory: () => apiFetch("/checkins/history/"),
  saveCheckIn: (payload: Record<string, unknown>) => apiFetch("/checkins/", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
  latestRecommendation: () => apiFetch("/recommendations/latest/"),
  recommendationHistory: () => apiFetch("/recommendations/history/"),
  generateRecommendation: () => apiFetch<{ success: boolean; data: unknown }>("/recommendations/generate/", {
    method: "POST",
    body: JSON.stringify({}),
  }),
};
