/**
 * Selectors for auth store - provides reusable, testable state selections
 * Uses backend-generated User type with OAuth properties
 */
import type { AuthStore, User } from './types';

// Basic selectors for direct state access
export const selectUser = (state: AuthStore): User | null => state.user;
export const selectIsAuthenticated = (state: AuthStore): boolean => state.isAuthenticated;
export const selectIsLoading = (state: AuthStore): boolean => state.isLoading;
export const selectError = (state: AuthStore): string | null => state.error;
export const selectSessionToken = (state: AuthStore): string | null => state.sessionToken;

// Computed selectors for derived state
export const selectUserName = (state: AuthStore): string => 
  state.user?.oauth_name || state.user?.oauth_username || 'Guest';

export const selectUserAvatar = (state: AuthStore): string | null | undefined =>
  state.user?.oauth_avatar_url;

export const selectHasSession = (state: AuthStore): boolean => 
  !!state.sessionToken && state.isAuthenticated;

export const selectIsInitialized = (state: AuthStore): boolean => 
  !state.isLoading || state.isAuthenticated;

// Grouped selectors for related data
export const selectAuthState = (state: AuthStore) => ({
  user: state.user,
  isAuthenticated: state.isAuthenticated,
  isLoading: state.isLoading,
  error: state.error,
  sessionToken: state.sessionToken,
});

export const selectAuthActions = (state: AuthStore) => ({
  loginWithGithub: state.loginWithGithub,
  logout: state.logout,
  refreshSession: state.refreshSession,
  updateUser: state.updateUser,
  initializeAuth: state.initializeAuth,
});

export const selectUserProfile = (state: AuthStore) => ({
  id: state.user?.id,
  email: state.user?.oauth_email,
  name: state.user?.oauth_name,
  username: state.user?.oauth_username,
  avatar: state.user?.oauth_avatar_url,
  provider: state.user?.oauth_provider,
});

// Status selectors for UI state
export const selectAuthStatus = (state: AuthStore) => {
  if (state.isLoading) return 'loading' as const;
  if (state.error) return 'error' as const;
  if (state.isAuthenticated) return 'authenticated' as const;
  return 'unauthenticated' as const;
};

export const selectCanRefreshSession = (state: AuthStore): boolean =>
  state.isAuthenticated && !!state.sessionToken && !state.isLoading;
