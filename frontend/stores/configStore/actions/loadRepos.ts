// Load repos action
import type { StateCreator } from '@/lib/zustand';
import { ReposService } from '@/services/repos/reposService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createLoadReposAction: StateCreator<
  ConfigStore,
  [],
  [],
  { loadRepos: () => Promise<void> }
> = (set) => {
  return {
    loadRepos: async () => {
      logStoreAction('ConfigStore', 'loadRepos');
      
      set((draft) => {
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/loadRepos/start');

      try {
        const reposResponse = await ReposService.getAvailableRepos();
        
        set((draft) => {
          draft.availableRepos = reposResponse.repositories || [];
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/loadRepos/success');
      } catch (error) {
        const storeError = handleStoreError(error, 'loadRepos');
        console.error('Load repos error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/loadRepos/error');
      }
    },
  };
};