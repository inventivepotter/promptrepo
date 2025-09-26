// Types for Auth Store - Direct proxy to backend-generated types
import type { components } from '@/types/generated/api';

// Direct re-export of backend types - no conversions
export type User = components['schemas']['User'];
export type LoginResponseData = components['schemas']['LoginResponseData'];
export type AuthUrlResponseData = components['schemas']['AuthUrlResponseData'];

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthActions {
  login: (customRedirectUrl?: string) => void; // Initial GitHub OAuth redirect
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  updateUser: (updates: Partial<User>) => void;
  initializeAuth: () => Promise<void>;
  handleAuthSuccess: (user: User) => void;
  
  // Internal actions
  setLoading: (loading: boolean) => void;
  setUser: (user: User | null) => void;
  setError: (error: string | null) => void;
}

export type AuthStore = AuthState & AuthActions;

// Storage configuration
export interface AuthPersistConfig {
  storage: 'sessionStorage' | 'localStorage';
  partialize: (state: AuthStore) => Partial<AuthStore>;
}