// Initial state for Auth Store
import type { AuthState } from './types';

export const initialAuthState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  promptrepoRedirectUrl: '/',
};