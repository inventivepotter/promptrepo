// Initialize auth action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';
import { authService } from '@/services/auth/authService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';

export const createInitializeAuthAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'initializeAuth'>
> = (set, get) => ({
  initializeAuth: async () => {
    const state = get();
    
    // Skip if already initialized or currently initializing
    if (state.isInitialized || state.isInitializing) {
      logStoreAction('AuthStore', 'initializeAuth - skipped (already initialized or in progress)');
      return;
    }
    
    logStoreAction('AuthStore', 'initializeAuth');
    
    set((draft) => {
      draft.isInitializing = true;
      draft.isLoading = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/initialize/start');
    
    try {
      // Check authentication status using httpOnly cookie verification
      const { success, user } = await authService.checkAuthStatus();
      
      if (success && user) {
        set((draft) => {
          draft.user = user;
          draft.isAuthenticated = true;
          draft.isLoading = false;
          draft.isInitialized = true;
          draft.isInitializing = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'auth/initialize/success');
      } else {
        set((draft) => {
          draft.user = null;
          draft.isAuthenticated = false;
          draft.isLoading = false;
          draft.isInitialized = true;
          draft.isInitializing = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'auth/initialize/no-session');
      }
    } catch (error) {
      const storeError = handleStoreError(error, 'initializeAuth');
      console.error('Failed to initialize auth:', error);
      
      set((draft) => {
        draft.user = null;
        draft.isAuthenticated = false;
        draft.isLoading = false;
        draft.error = storeError.message;
        draft.isInitialized = true;
        draft.isInitializing = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'auth/initialize/error');
    }
  },
});