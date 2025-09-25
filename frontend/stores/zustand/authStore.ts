import { create } from 'zustand';
import { devtools, persist, immer, createSessionStorage } from '@/lib/zustand';
import type { AuthState, AuthUser } from '@/types/stores';

// =============================================================================
// Auth Store Implementation
// =============================================================================

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Initial State
        user: null,
        isAuthenticated: false,
        isLoading: false,
        sessionToken: null,
        error: null,

        // Actions
        loginWithGithub: async (code: string, state?: string) => {
          set((draft) => {
            draft.isLoading = true;
            draft.error = null;
          });
          
          try {
            const { authService } = await import('@/services/auth/authService');
            const response = await authService.handleCallback(code, state || '');
            
            if (response) {
              // Store the session token and user data
              set((draft) => {
                draft.sessionToken = response.sessionToken;
                draft.isAuthenticated = true;
                if (response.user) {
                  draft.user = {
                    id: response.user.id || '',
                    name: response.user.oauth_name || response.user.oauth_username || '',
                    email: response.user.oauth_email || '',
                    github: response.user.oauth_provider === 'github' ? {
                      username: response.user.oauth_username || '',
                      accessToken: '',  // Token is managed by authService
                    } : undefined
                  };
                }
                draft.isLoading = false;
              });
            } else {
              throw new Error('GitHub authentication failed');
            }
          } catch (error) {
            set((draft) => {
              draft.isLoading = false;
              draft.error = error instanceof Error ? error.message : 'GitHub login failed';
            });
            throw error;
          }
        },

        logout: async () => {
          set((draft) => {
            draft.isLoading = true;
          });
          
          try {
            const { authService } = await import('@/services/auth/authService');
            await authService.logout();
          } finally {
            // Clear session storage
            sessionStorage.removeItem('auth-store');
            
            set((draft) => {
              draft.user = null;
              draft.sessionToken = null;
              draft.isAuthenticated = false;
              draft.isLoading = false;
              draft.error = null;
            });
          }
        },

        refreshSession: async () => {
          const currentToken = get().sessionToken;
          if (!currentToken) return;
          
          set((draft) => {
            draft.isLoading = true;
          });
          
          try {
            const { authService } = await import('@/services/auth/authService');
            const { success, user } = await authService.refreshSession();
            
            if (success && user) {
              set((draft) => {
                draft.user = {
                  id: user.id || '',
                  name: user.oauth_name || user.oauth_username || '',
                  email: user.oauth_email || '',
                  github: user.oauth_provider === 'github' ? {
                    username: user.oauth_username || '',
                    accessToken: '',  // Token is managed by authService
                  } : undefined
                };
                draft.sessionToken = authService.getSessionToken();
                draft.isAuthenticated = authService.isAuthenticated();
                draft.isLoading = false;
              });
            } else {
              // Session expired or invalid, logout
              get().logout();
            }
          } catch (error) {
            console.error('Session refresh failed:', error);
            set((draft) => {
              draft.isLoading = false;
              draft.error = error instanceof Error ? error.message : 'Session refresh failed';
            });
            get().logout();
          }
        },

        updateUser: (updates: Partial<AuthUser>) => {
          const { user } = get();
          if (!user) return;
          
          set((draft) => {
            if (draft.user) {
              Object.assign(draft.user, updates);
            }
          });
        },

        // Internal actions
        setLoading: (loading: boolean) => {
          set((draft) => {
            draft.isLoading = loading;
          });
        },

        setUser: (user: AuthUser | null) => {
          set((draft) => { 
            draft.user = user;
            draft.isAuthenticated = !!user;
          });
        },

        setSessionToken: (token: string | null) => {
          set((draft) => { 
            draft.sessionToken = token;
            draft.isAuthenticated = !!token;
          });
        },

        setError: (error: string | null) => {
          set((draft) => {
            draft.error = error;
          });
        },

        // Initialize auth state from authService
        initializeAuth: async () => {
          set((draft) => {
            draft.isLoading = true;
          });
          
          try {
            const { authService } = await import('@/services/auth/authService');
            
            // Check if we have a session token
            const sessionToken = authService.getSessionToken();
            if (sessionToken) {
              // Try to get user data
              const user = await authService.getUser();
              
              set((draft) => {
                draft.sessionToken = sessionToken;
                draft.isAuthenticated = authService.isAuthenticated();
                if (user) {
                  draft.user = {
                    id: user.id || '',
                    name: user.oauth_name || user.oauth_username || '',
                    email: user.oauth_email || '',
                    github: user.oauth_provider === 'github' ? {
                      username: user.oauth_username || '',
                      accessToken: '',
                    } : undefined
                  };
                }
                draft.isLoading = false;
              });
            } else {
              set((draft) => {
                draft.isLoading = false;
              });
            }
          } catch (error) {
            console.error('Failed to initialize auth:', error);
            set((draft) => {
              draft.isLoading = false;
              draft.error = error instanceof Error ? error.message : 'Failed to initialize auth';
            });
          }
        },
      })),
      {
        name: 'auth-store',
        storage: createSessionStorage(),
        partialize: (state) => ({
          user: state.user,
          sessionToken: state.sessionToken,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    {
      name: 'Auth Store',
    }
  )
);

// =============================================================================
// Store Selectors
// =============================================================================

export const useAuthActions = () => useAuthStore((state) => ({
  loginWithGithub: state.loginWithGithub,
  logout: state.logout,
  refreshSession: state.refreshSession,
  updateUser: state.updateUser,
  setLoading: state.setLoading,
  setUser: state.setUser,
  setSessionToken: state.setSessionToken,
  setError: state.setError,
  initializeAuth: state.initializeAuth,
}));

export const useAuthState = () => useAuthStore((state) => ({
  user: state.user,
  isAuthenticated: state.isAuthenticated,
  isLoading: state.isLoading,
  sessionToken: state.sessionToken,
  error: state.error,
}));

export const useUser = () => useAuthStore((state) => state.user);
export const useIsAuthenticated = () => useAuthStore((state) => state.isAuthenticated);
export const useAuthLoading = () => useAuthStore((state) => state.isLoading);
export const useAuthError = () => useAuthStore((state) => state.error);