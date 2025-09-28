// Handle GitHub OAuth callback by getting search params from current URL
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';

export const createHandleGithubCallbackAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'handleGithubCallback'>
> = (set, get) => ({
  handleGithubCallback: async () => {
    // Check if the callback has already been processed
    const state = get();
    if (state.githubCallbackProcessed) {
      return;
    }
    
    // Mark the callback as processed immediately to prevent race conditions
    // This prevents multiple simultaneous calls from the same browser instance
    set({ githubCallbackProcessed: true });
    
    try {
      // Get search parameters from current URL
      const searchParams = new URLSearchParams(window.location.search);
      
      // Use the existing processGithubCallback action
      await get().processGithubCallback(searchParams);
    } catch (error) {
      // If an error occurs, reset the flag to allow retry
      set({ githubCallbackProcessed: false });
      throw error;
    }
  },
});