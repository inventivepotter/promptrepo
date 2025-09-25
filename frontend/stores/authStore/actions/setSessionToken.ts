// Set session token action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';
import { logStoreAction } from '@/lib/zustand';

export const createSetSessionTokenAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'setSessionToken'>
> = (set) => ({
  setSessionToken: (token: string | null) => {
    logStoreAction('AuthStore', 'setSessionToken', { token: token ? '[REDACTED]' : null });
    
    set((draft) => {
      draft.sessionToken = token;
      draft.isAuthenticated = !!token;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/set-session-token');
  },
});