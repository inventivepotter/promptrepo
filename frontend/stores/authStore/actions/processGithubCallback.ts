// Process GitHub OAuth callback with search params and redirect
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';
import { errorNotification } from '@/lib/notifications';

export const createProcessGithubCallbackAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'processGithubCallback'>
> = (set, get) => ({
  processGithubCallback: async (searchParams: URLSearchParams) => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (!code || !state) {
      // If code or state is missing, silently redirect without showing error notification
      console.warn('GitHub callback missing code or state parameters');
      window.location.href = '/';
      return;
    }

    try {
      // Call the existing oauthCallbackGithub action
      await get().oauthCallbackGithub(code, state);
      
      // After the action completes, the store will have the redirect URL.
      const promptRepoRedirectUrl = get().promptrepoRedirectUrl;
      
      // Use window.location for redirect
      window.location.href = promptRepoRedirectUrl;
    } catch (err) {
      // Only show error notification for actual processing errors
      console.error('Callback processing error:', err);
      // Check if we should show an error notification (avoid duplicate notifications)
      const currentError = get().error;
      if (!currentError) {
        errorNotification('Authentication Error', 'An error occurred during authentication.');
      }
      window.location.href = '/';
    }
  },
});