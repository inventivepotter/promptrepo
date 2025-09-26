// Login with GitHub OAuth action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';
import { authService } from '@/services/auth/authService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import { errorNotification } from '@/lib/notifications';

export const createLoginWithGithubAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'oauthCallbackGithub'>
> = (set) => ({
  oauthCallbackGithub: async (code: string, stateParam?: string) => {
    logStoreAction('AuthStore', 'oauthCallbackGithub', { code, stateParam });
    
    set((draft) => {
      draft.isLoading = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/oauth/callback/github/start');
    
    try {
      const response = await authService.handleCallback(code, stateParam || '');
      
      if (response && response.user) {
        // With httpOnly cookies, we only need to store user data
        // The authentication cookie is already set by the backend
        set((draft) => {
          draft.user = response.user;
          draft.isAuthenticated = true;
          draft.isLoading = false;
          draft.promptrepoRedirectUrl = response.promptrepoRedirectUrl || '/';
    // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'auth/oauth/callback/github/success');
      } else {
        errorNotification(
          'Authentication Failed',
          'Could not complete GitHub authentication. Please try again.'
        );
      }
    } catch (error) {
      const storeError = handleStoreError(error, 'oauthCallbackGithub');
      set((draft) => {
        draft.isLoading = false;
        draft.error = storeError.message;
    // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'auth/oauth/callback/github/error');
      throw error;
    }
  },
});