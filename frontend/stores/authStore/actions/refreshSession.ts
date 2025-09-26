// Refresh session action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';
import { authService } from '@/services/auth/authService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';

export const createRefreshSessionAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'refreshSession'>
> = (set, get) => ({
  refreshSession: async () => {
    const currentUser = get().user;
    if (!currentUser) {
      console.warn('No user to refresh session for');
      return;
    }
    
    logStoreAction('AuthStore', 'refreshSession');
    
    set((draft) => {
      draft.isLoading = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/refresh/start');
    
    try {
      const { success, user } = await authService.refreshSession();
      
      if (success && user) {
        set((draft) => {
          draft.user = user;
          draft.isAuthenticated = true;
          draft.isLoading = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'auth/refresh/success');
      } else {
        // Session expired or invalid, logout
        set((draft) => {
          draft.user = null;
          draft.isAuthenticated = false;
          draft.isLoading = false;
          draft.error = 'Session expired';
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'auth/refresh/expired');
      }
    } catch (error) {
      const storeError = handleStoreError(error, 'refreshSession');
      console.error('Session refresh failed:', error);
      
      set((draft) => {
        draft.isLoading = false;
        draft.error = storeError.message;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'auth/refresh/error');
    }
  },
});