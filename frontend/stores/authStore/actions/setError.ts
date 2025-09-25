// Set error action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';
import { logStoreAction } from '@/lib/zustand';

export const createSetErrorAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'setError'>
> = (set) => ({
  setError: (error: string | null) => {
    logStoreAction('AuthStore', 'setError', { error });
    
    set((draft) => {
      draft.error = error;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/set-error');
  },
});