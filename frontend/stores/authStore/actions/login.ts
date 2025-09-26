// Login action - handles initial GitHub OAuth flow
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';

export const createLoginAction: StateCreator<
  AuthStore,
  [],
  [],
  { login: (customRedirectUrl?: string) => Promise<void> }
> = (set) => {

  return {
    login: async (customRedirectUrl?: string) => {
      try {
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
      } catch (error) {
        console.error('Login error:', error);
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