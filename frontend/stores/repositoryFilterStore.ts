import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { useShallow } from 'zustand/react/shallow';

/**
 * Repository Filter Store
 * 
 * Shared state for repository selection across prompts and tools pages.
 * Persists the selected repository across page navigation and browser sessions.
 */

interface RepositoryFilterState {
  selectedRepository: string;
}

interface RepositoryFilterActions {
  setSelectedRepository: (repository: string) => void;
  clearSelectedRepository: () => void;
}

export type RepositoryFilterStore = RepositoryFilterState & RepositoryFilterActions;

export const useRepositoryFilterStore = create<RepositoryFilterStore>()(
  persist(
    (set) => ({
      // State
      selectedRepository: '',

      // Actions
      setSelectedRepository: (repository: string) => {
        set({ selectedRepository: repository });
      },

      clearSelectedRepository: () => {
        set({ selectedRepository: '' });
      },
    }),
    {
      name: 'repository-filter-storage', // localStorage key
      partialize: (state) => ({ selectedRepository: state.selectedRepository }), // Only persist the selected repository
    }
  )
);

// Selectors
export const selectSelectedRepository = (state: RepositoryFilterStore) => state.selectedRepository;

// Hooks
export const useSelectedRepository = () => useRepositoryFilterStore(selectSelectedRepository);
export const useRepositoryFilterActions = () =>
  useRepositoryFilterStore(
    useShallow((state) => ({
      setSelectedRepository: state.setSelectedRepository,
      clearSelectedRepository: state.clearSelectedRepository,
    }))
  );