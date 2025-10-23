// Handle successful authentication action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore, User } from '../types';
import { logStoreAction } from '@/lib/zustand';

export const createHandleAuthSuccessAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'handleAuthSuccess'>
> = (set, get) => ({
  handleAuthSuccess: async (user: User) => {
    logStoreAction('AuthStore', 'handleAuthSuccess', { user: { id: user.id } });
    
    set((draft) => {
      draft.isLoading = false;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/success/start');
    
    // Call setUser which will handle cache invalidation
    await get().setUser(user);
    
    set((draft) => {
      draft.isAuthenticated = true;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/success/complete');
  },
});