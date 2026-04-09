import { createContext } from "react";
import type { User } from "../types/api";

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (provider: "google" | "apple", token: string, userName?: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthState | null>(null);
