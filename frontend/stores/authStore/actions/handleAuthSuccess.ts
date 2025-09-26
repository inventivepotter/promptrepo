// Handle successful authentication action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore, User } from '../types';
import { logStoreAction } from '@/lib/zustand';

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
  },
});