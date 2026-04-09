import { useState, useEffect, useCallback, type ReactNode } from "react";
import { setAccessToken, authExpiredEvent } from "../services/api";
import {
  loginWithApple as loginWithAppleService,
  loginWithGoogle as loginWithGoogleService,
  logoutFromServer,
  refreshAccessToken,
  clearTokens,
} from "../services/auth";
import type { User } from "../types/api";
import { AuthContext } from "./AuthContext";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    refreshAccessToken()
      .then((userData) => setUser(userData))
      .catch(() => clearTokens())
      .finally(() => setIsLoading(false));
  }, []);

  const login = useCallback(
    async (
      provider: "google" | "apple",
      token: string,
      userName?: string
    ) => {
      let response;
      if (provider === "google") {
        response = await loginWithGoogleService(token);
      } else {
        response = await loginWithAppleService(token, userName);
      }
      setAccessToken(response.access);
      localStorage.setItem("refresh_token", response.refresh);
      setUser(response.user);
    },
    []
  );

  const logout = useCallback(() => {
    logoutFromServer();
    clearTokens();
    setUser(null);
  }, []);

  useEffect(() => {
    const handleExpired = () => logout();
    authExpiredEvent.addEventListener("expired", handleExpired);
    return () => authExpiredEvent.removeEventListener("expired", handleExpired);
  }, [logout]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: user !== null,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
