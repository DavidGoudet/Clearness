const API_BASE = "/api";

export const authExpiredEvent = new EventTarget();

let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, data: unknown) {
    super(`API error: ${status}`);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
}

async function attemptRefresh(): Promise<boolean> {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_BASE}/auth/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) return false;

    const data = (await response.json()) as { access: string };
    setAccessToken(data.access);
    return true;
  } catch {
    return false;
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { method = "GET", body, headers: extraHeaders } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...extraHeaders,
  };

  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  const fetchOptions: RequestInit = {
    method,
    headers,
  };

  if (body !== undefined) {
    fetchOptions.body = JSON.stringify(body);
  }

  let response = await fetch(`${API_BASE}${path}`, fetchOptions);

  // On 401, attempt token refresh and retry once
  if (response.status === 401 && accessToken) {
    const refreshed = await attemptRefresh();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${accessToken}`;
      response = await fetch(`${API_BASE}${path}`, {
        ...fetchOptions,
        headers,
      });
    } else {
      authExpiredEvent.dispatchEvent(new Event("expired"));
    }
  }

  if (response.status === 204) {
    return undefined as T;
  }

  if (!response.ok) {
    let data: unknown;
    try {
      data = await response.json();
    } catch {
      data = null;
    }
    throw new ApiError(response.status, data);
  }

  return (await response.json()) as T;
}
