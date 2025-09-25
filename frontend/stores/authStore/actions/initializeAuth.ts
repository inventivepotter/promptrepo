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
> = (set) => ({
  initializeAuth: async () => {
    logStoreAction('AuthStore', 'initializeAuth');
    
    set((draft) => {
      draft.isLoading = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/initialize/start');
    
    try {
      // Check if we have a session token
      const sessionToken = authService.getSessionToken();
      if (sessionToken) {
        // Try to get user data
        const user = await authService.getUser();
        
        set((draft) => {
          draft.sessionToken = sessionToken;
          draft.user = user;
          draft.isAuthenticated = authService.isAuthenticated();
          draft.isLoading = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'auth/initialize/success');
      } else {
        set((draft) => {
          draft.isLoading = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'auth/initialize/no-session');
      }
    } catch (error) {
      const storeError = handleStoreError(error, 'initializeAuth');
      console.error('Failed to initialize auth:', error);
      
      set((draft) => {
        draft.isLoading = false;
        draft.error = storeError.message;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'auth/initialize/error');
    }
  },
});