// Types for Auth Store - Direct proxy to backend-generated types
import type { components } from '@/types/generated/api';

// Direct re-export of backend types - no conversions
export type User = components['schemas']['User'];
export type LoginResponseData = components['schemas']['LoginResponseData'];
export type RefreshResponseData = components['schemas']['RefreshResponseData'];
export type AuthUrlResponseData = components['schemas']['AuthUrlResponseData'];

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  sessionToken: string | null;
  error: string | null;
}

export interface AuthActions {
  loginWithGithub: (code: string, state?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
  initializeAuth: () => Promise<void>;
  
  // Internal actions
  setLoading: (loading: boolean) => void;
  setUser: (user: User | null) => void;
  setSessionToken: (token: string | null) => void;
  setError: (error: string | null) => void;
}

export type AuthStore = AuthState & AuthActions;

// Storage configuration
export interface AuthPersistConfig {
  storage: 'sessionStorage' | 'localStorage';
  partialize: (state: AuthStore) => Partial<AuthStore>;
}