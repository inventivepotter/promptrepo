// Login action - handles initial GitHub OAuth flow
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';
import { useLoadingStore } from '@/stores/loadingStore';

export const createLoginAction: StateCreator<
  AuthStore,
  [],
  [],
  { login: (customRedirectUrl?: string) => Promise<void> }
> = (set) => {

  return {
    login: async (customRedirectUrl?: string) => {
      try {
        // Show global loading overlay as soon as login starts
        useLoadingStore.getState().showLoading(
          'Signing in with GitHub',
          'Redirecting to GitHub for authentication...'
        );

        set((draft) => {
          draft.isLoading = true;
          draft.error = null;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'auth/login/start');

        // Build the login URL with optional redirect parameter
        const params = new URLSearchParams();
        if (customRedirectUrl) {
          params.append('promptrepo_redirect_url', customRedirectUrl);
        }
        
        const loginUrl = `/api/auth/login/github${params.toString() ? `?${params.toString()}` : ''}`;
        
        // Redirect to the Next.js API route which handles OAuth flow
        window.location.href = loginUrl;
        
        // Note: Loading overlay will remain visible through the redirect
        // It will be hidden by oauthCallbackGithub action after authentication completes
      } catch (error) {
        console.error('Login error:', error);
        
        // Hide loading overlay on error
        useLoadingStore.getState().hideLoading();
        
        set((draft) => {
          draft.isLoading = false;
          draft.error = 'Failed to initiate login';
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'auth/login/error');
        throw error;
      }
    },
  };
};