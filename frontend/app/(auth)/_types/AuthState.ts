import { User } from "../../../types/User";

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
  handleOAuthCallback: (sessionToken: string, expiresAt: string) => Promise<void>;
}

export interface LoginResponse {
  user: User;
  sessionToken: string;
  expiresAt: string;
}

export interface AuthSession {
  sessionToken: string;
  user: User;
  expiresAt: string;
}