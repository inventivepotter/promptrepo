// Update configured repos action
import type { StateCreator } from '@/lib/zustand';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore, RepoConfig } from '../types';

export const createUpdateConfiguredReposAction: StateCreator<
  ConfigStore,
  [],
  [],
  { updateConfiguredRepos: (repos: RepoConfig[]) => void }
> = (set) => {
  return {
    updateConfiguredRepos: (repos: RepoConfig[]) => {
      logStoreAction('ConfigStore', 'updateConfiguredRepos', { repos });
      
      try {
        set((draft) => {
          draft.config.repo_configs = repos;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/updateConfiguredRepos');
      } catch (error) {
        const storeError = handleStoreError(error, 'updateConfiguredRepos');
        console.error('Update configured repos error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/updateConfiguredRepos/error');
        
        throw error;
      }
    },
  };
};