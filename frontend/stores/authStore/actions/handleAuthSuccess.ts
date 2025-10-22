// Handle successful authentication action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore, User } from '../types';
import { logStoreAction } from '@/lib/zustand';
import { usePromptStore } from '@/stores/promptStore/store';
import { useConfigStore } from '@/stores/configStore/configStore';

export const createHandleAuthSuccessAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'handleAuthSuccess'>
> = (set) => ({
  handleAuthSuccess: (user: User) => {
    logStoreAction('AuthStore', 'handleAuthSuccess', { user: { id: user.id } });
    
    set((draft) => {
      draft.user = user;
      draft.isAuthenticated = true;
      draft.isLoading = false;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/success');
    
    // Invalidate both caches on successful login to fetch fresh user data
    console.log('Successful authentication - invalidating config and prompt caches');
    usePromptStore.getState().invalidateCache();
    useConfigStore.getState().invalidateCache();
  },
});