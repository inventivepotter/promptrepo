// Update user action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore, User } from '../types';
import { logStoreAction } from '@/lib/zustand';

export const createUpdateUserAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'updateUser'>
> = (set) => ({
  updateUser: (updates: Partial<User>) => {
    logStoreAction('AuthStore', 'updateUser', { updates });
    
    set((draft) => {
      if (draft.user) {
        draft.user = { ...draft.user, ...updates };
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/update-user');
  },
});