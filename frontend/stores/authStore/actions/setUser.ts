// Set user action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore, User } from '../types';
import { logStoreAction } from '@/lib/zustand';

export const createSetUserAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'setUser'>
> = (set) => ({
  setUser: (user: User | null) => {
    logStoreAction('AuthStore', 'setUser', { user: user ? { id: user.id } : null });
    
    set((draft) => {
      draft.user = user;
      draft.isAuthenticated = !!user;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/set-user');
  },
});