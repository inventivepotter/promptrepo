/**
 * Auth Store Public API
 * 
 * Centralized exports for the auth store module.
 * This file defines the public API surface of the auth store.
 */

// Main store
export { useAuthStore as default } from './store';
export { useAuthStore } from './store';

// Types
export type { 
  User,
  AuthState,
  AuthActions,
  AuthStore,
  LoginResponseData,
  AuthUrlResponseData,
  AuthPersistConfig
} from './types';

// Selectors
export {
  selectUser,
  selectIsAuthenticated,
  selectIsLoading,
  selectError,
  selectUserName,
  selectUserAvatar,
  selectHasSession,
  selectIsInitialized,
  selectAuthState,
  selectAuthActions,
  selectUserProfile,
  selectAuthStatus,
  selectCanRefreshSession
} from './selectors';

// Hooks
export {
  useUser,
  useIsAuthenticated,
  useAuthLoading,
  useAuthError,
  useAuthActions,
  useAuthState,
  useIsInitialized,
  useGithubCallbackStatus,
} from './hooks';

// Utilities
export {
  resetAuthStore,
  getAuthState,
  subscribeToAuth,
  subscribeToAuthProperty,
  waitForAuth,
  hasValidSession,
  getCurrentUser,
  logAuthState,
  setAuthStateForTesting
} from './utils';

/**
 * Example usage:
 * 
 * // In a React component
 * import { useAuth, selectUserName } from '@/stores/authStore/exports';
 * 
 * function MyComponent() {
 *   const { user, isAuthenticated, oauthCallbackGithub } = useAuth();
 *   // or
 *   const userName = useAuthStore(selectUserName);
 * }
 * 
 * // In a non-React context
 * import { getAuthState, subscribeToAuth } from '@/stores/authStore/exports';
 * 
 * const currentUser = getAuthState().user;
 * const unsubscribe = subscribeToAuth((state) => {
 *   console.log('Auth state changed:', state);
 * });
 */