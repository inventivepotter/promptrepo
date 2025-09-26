// Set available repos action
import type { StateCreator } from '@/lib/zustand';
import type { ConfigStore, RepoInfo } from '../types';

export const createSetAvailableReposAction: StateCreator<
  ConfigStore,
  [],
  [],
  { setAvailableRepos: (repos: RepoInfo[]) => void }
> = (set) => {
  return {
    setAvailableRepos: (repos: RepoInfo[]) => {
      set((draft) => {
        draft.availableRepos = repos;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/setAvailableRepos');
    },
  };
};