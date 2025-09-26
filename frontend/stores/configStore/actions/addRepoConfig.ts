// Add repo config action
import type { StateCreator } from '@/lib/zustand';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore, RepoConfig } from '../types';

export const createAddRepoConfigAction: StateCreator<
  ConfigStore,
  [],
  [],
  { addRepoConfig: (config: RepoConfig) => void }
> = (set) => {
  return {
    addRepoConfig: (config: RepoConfig) => {
      logStoreAction('ConfigStore', 'addRepoConfig', config);
      
      try {
        set((draft) => {
          const currentConfigs = draft.config.repo_configs || [];
          draft.config.repo_configs = [...currentConfigs, config];
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/addRepoConfig');
      } catch (error) {
        const storeError = handleStoreError(error, 'addRepoConfig');
        console.error('Add repo config error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/addRepoConfig/error');
        
        throw error;
      }
    },
  };
};