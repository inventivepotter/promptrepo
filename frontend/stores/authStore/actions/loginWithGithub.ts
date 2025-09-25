// Login with GitHub OAuth action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';
import { authService } from '@/services/auth/authService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';

export const createLoginWithGithubAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'loginWithGithub'>
> = (set) => ({
  loginWithGithub: async (code: string, stateParam?: string) => {
    logStoreAction('AuthStore', 'loginWithGithub', { code, stateParam });
    
    set((draft) => {
      draft.isLoading = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/login/github/start');
    
    try {
      const response = await authService.handleCallback(code, stateParam || '');
      
      if (response) {
        // Store the session token and user data directly from backend
        set((draft) => {
          draft.sessionToken = response.sessionToken;
          draft.user = response.user;
          draft.isAuthenticated = true;
          draft.isLoading = false;
    // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'auth/login/github/success');
      } else {
        throw new Error('GitHub authentication failed');
      }
    } catch (error) {
      const storeError = handleStoreError(error, 'loginWithGithub');
      set((draft) => {
        draft.isLoading = false;
        draft.error = storeError.message;
    // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'auth/login/github/error');
      throw error;
    }
  },
});