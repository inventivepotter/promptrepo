import { useState, useRef, useCallback } from 'react';
import { AuthState, AuthContextType } from '../_types/AuthState';
import { getAuthUrl } from '../_lib/getAuthUrl';
import { getAuthUser } from '../_lib/getAuthUser';
import { handleLogout } from '../_lib/handleLogout';
import { handleAuthCallback } from '../_lib/handleAuthCallback';
import { refreshAuthSession } from '../_lib/refreshAuthSession';
import { storageState } from './storageState';

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
  return storageState.getInitialState();
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
      const storedState = storageState.getInitialState();
      
      // If we have a stored session, verify it
      if (storedState.sessionToken) {
        const user = await getAuthUser();
        
        if (user) {
          updateAuthState({
            isAuthenticated: true,
            isLoading: false,
            user,
            sessionToken: storedState.sessionToken,
          });
        } else {
          // Invalid session - clear everything
          storageState.clearSession();
          storageState.clearUserData();
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
      storageState.clearSession();
      storageState.clearUserData();
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
  const login = useCallback(async () => {
    try {
      updateAuthState(prev => ({ ...prev, isLoading: true }));
      
      const authUrl = await getAuthUrl();
      // TODO: Remove after Auth testing
      // In development, directly handle the mock auth callback
      if (process.env.NODE_ENV === 'development') {
        const result = await handleAuthCallback('mock_code', 'mock_state');
        if (result) {
          updateAuthState({
            isAuthenticated: true,
            isLoading: false,
            user: result.user,
            sessionToken: result.sessionToken,
          });
          return;
        }
      }
      // TODO: Remove after Auth testing
      if (authUrl && process.env.NODE_ENV !== 'development') {
        window.location.href = authUrl;
      } else {
        throw new Error('Failed to get auth URL');
      }
    } catch (error) {
      console.error('Login failed:', error);
      updateAuthState(prev => ({ ...prev, isLoading: false }));
      throw error;
    }
  }, [updateAuthState]);

  // Handle OAuth callback
  const handleOAuthCallback = useCallback(async (sessionToken: string, expiresAt: string) => {
    try {
      updateAuthState(prev => ({ ...prev, isLoading: true }));

      const result = await handleAuthCallback(sessionToken, expiresAt);
      
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
      
      const success = await handleLogout();
      
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