// Hooks for selective subscriptions to auth store
import { useAuthStore } from './store';

// Hook for user data
export const useUser = () => useAuthStore((state) => state.user);

// Hook for authentication status
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated);

// Hook for loading state
export const useAuthLoading = () => useAuthStore((state) => state.isLoading);

// Hook for error state
export const useAuthError = () => useAuthStore((state) => state.error);

// Hook for session token
export const useSessionToken = () => useAuthStore((state) => state.sessionToken);

// Hook for auth actions
export const useAuthActions = () => {
  const {
    loginWithGithub,
    logout,
    refreshSession,
    updateUser,
    initializeAuth,
  } = useAuthStore();
  
  return {
    loginWithGithub,
    logout,
    refreshSession,
    updateUser,
    initializeAuth,
  };
};

// Hook for complete auth state
export const useAuthState = () => {
  const user = useUser();
  const isAuthenticated = useIsAuthenticated();
  const isLoading = useAuthLoading();
  const error = useAuthError();
  const sessionToken = useSessionToken();
  
  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    sessionToken,
  };
};
