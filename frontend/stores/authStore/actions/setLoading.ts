// Set loading state action
import type { StateCreator } from '@/lib/zustand';
import type { AuthStore } from '../types';
import { logStoreAction } from '@/lib/zustand';

export const createSetLoadingAction: StateCreator<
  AuthStore,
  [],
  [],
  Pick<AuthStore, 'setLoading'>
> = (set) => ({
  setLoading: (loading: boolean) => {
    logStoreAction('AuthStore', 'setLoading', { loading });
    
    set((draft) => {
      draft.isLoading = loading;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'auth/set-loading');
  },
});