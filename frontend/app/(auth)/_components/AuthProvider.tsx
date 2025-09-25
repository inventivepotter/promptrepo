'use client';

import React, { createContext, useContext, useEffect, useRef } from 'react';
import { AuthContextType } from '../_types/AuthState';
import { useAuthState } from '../_state/authState';
import * as authStore from '@/stores/authStore_old';

// Create Auth Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth Provider Component
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const auth = useAuthState();
  const hasInitialized = useRef(false);
  const checkTimer = useRef<NodeJS.Timeout | null>(null);

  // Initialize auth state once on mount
  useEffect(() => {
    // Skip if already initialized
    if (hasInitialized.current) return;
    
    // Get initial state from storage
    const storedState = authStore.getInitialAuthState();
    if (storedState.isAuthenticated) {
      // Only verify session if we have stored credentials
      auth.checkAuth();
    }
    hasInitialized.current = true;

  }, []); // Empty dependency array as this should only run once on mount

  // Handle storage changes and periodic refresh
  useEffect(() => {
    // Only set up refresh timer if authenticated
    if (auth.isAuthenticated && !checkTimer.current) {
      checkTimer.current = setInterval(() => {
        if (authStore.shouldRefreshSession()) {
          auth.checkAuth();
        }
      }, 5 * 60 * 1000); // Check every 5 minutes
    }

    // Listen for storage changes from other tabs/windows
    const handleStorageChange = (e: StorageEvent) => {
      if (!e.key?.includes('auth_') && !e.key?.includes('user_')) return;
      
      const currentState = authStore.getInitialAuthState();
      const hasStateChanged = (
        currentState.isAuthenticated !== auth.isAuthenticated ||
        currentState.sessionToken !== auth.sessionToken
      );

      if (hasStateChanged && !auth.isLoading) {
        auth.checkAuth();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Cleanup
    return () => {
      window.removeEventListener('storage', handleStorageChange);
      if (checkTimer.current) {
        clearInterval(checkTimer.current);
        checkTimer.current = null;
      }
    };
  }, [auth.isAuthenticated, auth.sessionToken, auth.isLoading]);

  return (
    <AuthContext.Provider value={auth}>
      {children}
    </AuthContext.Provider>
  );
}

// Custom hook to use auth context
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export default AuthProvider;