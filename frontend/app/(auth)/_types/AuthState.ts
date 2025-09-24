import type { components } from "@/types/generated/api";

export type User = components['schemas']['User'];
export type LoginResponse = components['schemas']['LoginResponseData'];

export interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: User | null;
  sessionToken: string | null;
}

export interface AuthContextType extends AuthState {
  login: () => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  handleOAuthCallback: (code: string, state: string) => Promise<void>;
}

export interface AuthSession {
  sessionToken: string;
  user: User;
  expiresAt: string;
}