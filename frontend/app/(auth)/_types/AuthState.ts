export interface User {
  id: string;
  username: string;
  name: string;
  email: string;
  avatar_url: string;
  github_id: string | null;
  html_url: string | null;
  sessions: unknown;
}

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