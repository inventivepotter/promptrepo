// Set user action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore, User } from '../types';
import { logStoreAction } from '@/lib/zustand';
import { usePromptStore } from '@/stores/promptStore/store';
import { useConfigStore } from '@/stores/configStore/configStore';

export const createSetUserAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'setUser'>
> = (set) => ({
  setUser: async (user: User | null) => {
    logStoreAction('AuthStore', 'setUser', { user: user ? { id: user.id } : null });
    
    set((draft) => {
      draft.user = user;
      draft.isAuthenticated = !!user;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/set-user');
    
    // Invalidate and refresh config and prompt caches when user changes
    // Both invalidateCache() methods now clear cache AND fetch fresh data
    if (user) {
      console.log('User set - invalidating and refreshing config and prompt caches');
      await useConfigStore.getState().invalidateCache();
      await usePromptStore.getState().invalidateCache();
    }
  },
});