// Logout action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';
import { authService } from '@/services/auth/authService';
import { logStoreAction } from '@/lib/zustand';

export const createLogoutAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'logout'>
> = (set) => ({
  logout: async () => {
    logStoreAction('AuthStore', 'logout');
    
    set((draft) => {
      draft.isLoading = true;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/logout/start');
    
    try {
      await authService.logout();
    } finally {
      // Clear session storage
      sessionStorage.removeItem('auth-store');
      
      // Reset state to initial values
      set((draft) => {
        draft.user = null;
        draft.isAuthenticated = false;
        draft.isLoading = false;
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'auth/logout/complete');
    }
  },
});