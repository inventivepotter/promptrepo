import { useState, useRef, useCallback } from 'react';
import { AuthState, AuthContextType } from '../_types/AuthState';
import { authService } from '@/services/auth/authService';
import * as authStore from '@/stores/authStore_old';
import { errorNotification } from '@/lib/notifications';

// Initialize with stored auth state if available
const getInitialAuthState = (): AuthState => {
  if (typeof window === 'undefined') {
    return {
      isAuthenticated: false,
      isLoading: true,
      user: null,
      sessionToken: null,
    };
  }
  return authStore.getInitialAuthState();
};

export function useAuthState(): AuthContextType {
  const [authState, setAuthState] = useState<AuthState>(getInitialAuthState);
  const isCheckingAuth = useRef(false);
  const initialCheckDone = useRef(false);

  const updateAuthState = useCallback((updater: AuthState | ((prev: AuthState) => AuthState)) => {
    setAuthState(prev => {
      const newState = typeof updater === 'function' ? updater(prev) : updater;
      return newState;
    });
  }, []);

  // Check authentication status
  const checkAuth = useCallback(async () => {
    // Skip if already checking
    if (isCheckingAuth.current) return;
    isCheckingAuth.current = true;

    try {
      // Get initial state from storage
      const storedState = authStore.getInitialAuthState();
      
      // If we have a stored session, verify it
      if (storedState.sessionToken) {
        const user = await authService.getUser();
        
        if (user) {
          updateAuthState({
            isAuthenticated: true,
            isLoading: false,
            user,
            sessionToken: storedState.sessionToken,
          });
        } else {
          // Invalid session - clear everything
          authStore.clearSession();
          authStore.clearUserData();
          updateAuthState({
            isAuthenticated: false,
            isLoading: false,
            user: null,
            sessionToken: null,
          });
        }
      } else {
        // No stored session
        updateAuthState({
          isAuthenticated: false,
          isLoading: false,
          user: null,
          sessionToken: null,
        });
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      // Clear everything on error
      authStore.clearSession();
      authStore.clearUserData();
      updateAuthState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        sessionToken: null,
      });
    } finally {
      isCheckingAuth.current = false;
      initialCheckDone.current = true;
    }
  }, [updateAuthState]);

  // Initiate login flow
  const login = useCallback(async (redirectUrl?: string) => {
    try {
      updateAuthState(prev => ({ ...prev, isLoading: true }));

      // Use provided redirect URL or current pathname
      const promptrepoRedirectUrl = redirectUrl || window.location.pathname;
      const authUrl = await authService.getAuthUrl(promptrepoRedirectUrl);

      if (authUrl) {
        window.location.href = authUrl;
      } else {
        errorNotification('Login Failed', 'Unable to initiate login. Please try again.');
      }
    } catch (error) {
      console.error('Login failed:', error);
      updateAuthState(prev => ({ ...prev, isLoading: false }));
      errorNotification('Login Failed', 'Unable to initiate login. Please try again.');
    }
  }, [updateAuthState]);

  // Handle OAuth callback
  const handleOAuthCallback = useCallback(async (code: string, state: string) => {
    try {
      updateAuthState(prev => ({ ...prev, isLoading: true }));

      const result = await authService.handleCallback(code, state);
      
      if (result) {
        updateAuthState({
          isAuthenticated: true,
          isLoading: false,
          user: result.user,
          sessionToken: result.sessionToken,
        });
      } else {
        throw new Error('Failed to complete authentication');
      }
    } catch (error) {
      console.error('OAuth callback failed:', error);
      updateAuthState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        sessionToken: null,
      });
      throw error;
    }
  }, [updateAuthState]);

  // Logout
  const logout = useCallback(async () => {
    try {
      updateAuthState(prev => ({ ...prev, isLoading: true }));
      
      const success = await authService.logout();
      
      if (success) {
        updateAuthState({
          isAuthenticated: false,
          isLoading: false,
          user: null,
          sessionToken: null,
        });
      }
    } catch (error) {
      console.error('Logout failed:', error);
      // Still clear state even if backend logout fails
      updateAuthState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
        sessionToken: null,
      });
    }
  }, [updateAuthState]);

  return {
    ...authState,
    login,
    logout,
    checkAuth,
    handleOAuthCallback,
  };
}

// Custom hook for accessing auth context
export function useAuth(): AuthContextType {
  return useAuthState();
}