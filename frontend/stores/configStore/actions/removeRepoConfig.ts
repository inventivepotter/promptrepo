// Remove repo config action
import type { StateCreator } from '@/lib/zustand';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createRemoveRepoConfigAction: StateCreator<
  ConfigStore,
  [],
  [],
  { removeRepoConfig: (index: number) => void }
> = (set) => {
  return {
    removeRepoConfig: (index: number) => {
      logStoreAction('ConfigStore', 'removeRepoConfig', { index });
      
      try {
        set((draft) => {
          if (draft.config.repo_configs && index >= 0 && index < draft.config.repo_configs.length) {
            draft.config.repo_configs.splice(index, 1);
          }
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/removeRepoConfig');
      } catch (error) {
        const storeError = handleStoreError(error, 'removeRepoConfig');
        console.error('Remove repo config error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/removeRepoConfig/error');
        
        throw error;
      }
    },
  };
};