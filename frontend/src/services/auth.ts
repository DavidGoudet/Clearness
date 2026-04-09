import { apiRequest, setAccessToken } from "./api";
import type { AuthResponse, TokenRefreshResponse, User } from "../types/api";

export async function loginWithGoogle(idToken: string): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/auth/google/", {
    method: "POST",
    body: { id_token: idToken },
  });
}

export async function loginWithApple(
  identityToken: string,
  userName?: string
): Promise<AuthResponse> {
  return apiRequest<AuthResponse>("/auth/apple/", {
    method: "POST",
    body: { identity_token: identityToken, user_name: userName ?? "" },
  });
}

export async function refreshAccessToken(): Promise<User> {
  const refreshToken = getStoredRefreshToken();
  if (!refreshToken) {
    throw new Error("No refresh token stored");
  }

  const tokenResponse = await apiRequest<TokenRefreshResponse>(
    "/auth/refresh/",
    {
      method: "POST",
      body: { refresh: refreshToken },
    }
  );

  setAccessToken(tokenResponse.access);

  const user = await apiRequest<User>("/me/");
  return user;
}

export async function logoutFromServer(): Promise<void> {
  const refreshToken = getStoredRefreshToken();
  if (!refreshToken) return;

  try {
    await apiRequest("/auth/logout/", {
      method: "POST",
      body: { refresh: refreshToken },
    });
  } catch {
    // Fire-and-forget: server logout failure should not block client cleanup
  }
}

export function clearTokens(): void {
  localStorage.removeItem("refresh_token");
  setAccessToken(null);
}

export function getStoredRefreshToken(): string | null {
  return localStorage.getItem("refresh_token");
}
