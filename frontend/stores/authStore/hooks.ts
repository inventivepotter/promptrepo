// Hooks for selective subscriptions to auth store
import { useShallow } from 'zustand/react/shallow';
import { useAuthStore } from './store';
import type { AuthActions } from './types';

// Hook for user data
export const useUser = () => useAuthStore((state) => state.user);

// Hook for authentication status
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated);

// Hook for loading state
export const useAuthLoading = () => useAuthStore((state) => state.isLoading);

// Hook for error state
export const useAuthError = () => useAuthStore((state) => state.error);

// Hook for initialization status
export const useIsInitialized = () => useAuthStore((state) => state.isInitialized);

// Hook for auth actions - optimized to prevent re-renders
// Actions are stable references, so we can cache them
let cachedActions: Pick<AuthActions, 'login' | 'logout' | 'oauthCallbackGithub' | 'processGithubCallback' | 'handleGithubCallback' | 'refreshSession' | 'updateUser' | 'initializeAuth'> | null = null;
export const useAuthActions = () => {
  if (!cachedActions) {
    const store = useAuthStore.getState();
    cachedActions = {
      login: store.login,
      logout: store.logout,
      oauthCallbackGithub: store.oauthCallbackGithub,
      processGithubCallback: store.processGithubCallback,
      handleGithubCallback: store.handleGithubCallback,
      refreshSession: store.refreshSession,
      updateUser: store.updateUser,
      initializeAuth: store.initializeAuth,
    };
  }
  return cachedActions;
};

// Hook for complete auth state - use shallow equality
export const useAuthState = () => {
  return useAuthStore(
    useShallow((state) => ({
      user: state.user,
      isAuthenticated: state.isAuthenticated,
      isLoading: state.isLoading,
      error: state.error,
      isInitialized: state.isInitialized,
    }))
  );
};

// Hook for GitHub callback status
export const useGithubCallbackStatus = () => {
  return useAuthStore(
    useShallow((state) => ({
      processed: state.githubCallbackProcessed,
      error: state.error,
      isLoading: state.isLoading,
    }))
  );
};
