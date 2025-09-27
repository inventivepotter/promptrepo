// Load repos action
import type { StateCreator } from '@/lib/zustand';
import { ReposService } from '@/services/repos/reposService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createLoadReposAction: StateCreator<
  ConfigStore,
  [],
  [],
  { loadAvailableRepos: () => Promise<void> }
> = (set, get) => {
  return {
    loadAvailableRepos: async () => {
      logStoreAction('ConfigStore', 'loadAvailableRepos');
      
      set((draft) => {
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/loadAvailableRepos/start');

      try {
        // Check if we already have repos data (from localStorage hydration)
        const currentState = get();
        if (currentState.availableRepos && currentState.availableRepos.length > 0) {
          // We have valid repos data, no need to call API
          logStoreAction('ConfigStore', 'loadAvailableRepos/skip - data from localStorage');
          return;
        }

        const reposResponse = await ReposService.getAvailableRepos();
        
        set((draft) => {
          draft.availableRepos = reposResponse.repositories || [];
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/loadAvailableRepos/success');
      } catch (error) {
        const storeError = handleStoreError(error, 'loadAvailableRepos');
        console.error('Load repos error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/loadAvailableRepos/error');
      }
    },
  };
};