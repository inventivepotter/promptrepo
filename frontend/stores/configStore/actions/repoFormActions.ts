// Repo form actions for managing repository configuration form state
import type { StateCreator } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createRepoFormActions: StateCreator<
  ConfigStore,
  [],
  [],
  {
    setSelectedRepo: (repo: string) => void;
    setSelectedRepoWithSideEffects: (repo: string) => Promise<void>;
    setSelectedBranch: (branch: string) => void;
    setIsSaving: (saving: boolean) => void;
    setRepoSearchValue: (value: string) => void;
    setBranchSearchValue: (value: string) => void;
    resetRepoForm: () => void;
  }
> = (set, get) => {
  return {
    setSelectedRepo: (repo: string) => {
      set((draft) => {
        draft.selectedRepo = repo;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/setSelectedRepo');
    },

    setSelectedRepoWithSideEffects: async (repo: string) => {
      // First set the selected repo
      set((draft) => {
        draft.selectedRepo = repo;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/setSelectedRepoWithSideEffects');

      // If a repo is selected, fetch its branches and reset branch-related state
      if (repo) {
        const [owner, repoName] = repo.split('/');
        await get().fetchBranches(owner, repoName);
        
        // Reset selected branch and search value when repo changes
        set((draft) => {
          draft.selectedBranch = '';
          draft.branchSearchValue = '';
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/resetBranchState');
      } else {
        // If no repo is selected, reset branches
        get().resetBranches();
      }
    },

    setSelectedBranch: (branch: string) => {
      set((draft) => {
        draft.selectedBranch = branch;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/setSelectedBranch');
    },

    setIsSaving: (saving: boolean) => {
      set((draft) => {
        draft.isSaving = saving;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/setIsSaving');
    },

    setRepoSearchValue: (value: string) => {
      set((draft) => {
        draft.repoSearchValue = value;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/setRepoSearchValue');
    },

    setBranchSearchValue: (value: string) => {
      set((draft) => {
        draft.branchSearchValue = value;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/setBranchSearchValue');
    },

    resetRepoForm: () => {
      set((draft) => {
        draft.selectedRepo = '';
        draft.selectedBranch = '';
        draft.isSaving = false;
        draft.repoSearchValue = '';
        draft.branchSearchValue = '';
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/resetRepoForm');
    },
  };
};