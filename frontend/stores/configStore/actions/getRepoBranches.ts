// Get repo branches action for fetching available branches for a repository
import type { StateCreator } from '@/lib/zustand';
import { ReposService } from '@/services/repos/reposService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';
import type { components } from '@/types/generated/api';

type BranchInfo = components['schemas']['BranchInfo'];

export const createGetRepoBranchesAction: StateCreator<
  ConfigStore,
  [],
  [],
  { 
    fetchBranches: (owner: string, repo: string) => Promise<void>;
    resetBranches: () => void;
  }
> = (set, get) => {
  return {
    fetchBranches: async (owner: string, repo: string) => {
      logStoreAction('ConfigStore', 'fetchBranches');

      set((draft) => {
        draft.isLoadingBranches = true;
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/fetchBranches/start');

      try {
        const response = await ReposService.getBranches(owner, repo);
        const branches = response.branches || [];
        
        set((draft) => {
          draft.availableBranches = branches as BranchInfo[];
          draft.isLoadingBranches = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/fetchBranches/success');
      } catch (error) {
        const storeError = handleStoreError(error, 'fetchBranches');
        console.error('Fetch branches error:', error);

        set((draft) => {
          draft.availableBranches = [];
          draft.isLoadingBranches = false;
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/fetchBranches/error');
      }
    },

    resetBranches: () => {
      set((draft) => {
        draft.availableBranches = [];
        draft.isLoadingBranches = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/resetBranches');
    },
  };
};