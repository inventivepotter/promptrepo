import { useCallback, useMemo } from 'react';
import { Prompt } from '@/types/Prompt';
import { PromptsState } from '../_types/PromptState';

type PromptsStateUpdater = (
  updater: PromptsState | ((prev: PromptsState) => PromptsState), 
  shouldPersist?: boolean
) => void;

export interface PromptsListManagementFunctions {
  setSearchQuery: (query: string) => void;
  setCurrentPage: (page: number) => void;
  setSortBy: (sortBy: 'name' | 'updated_at', sortOrder: 'asc' | 'desc') => void;
  setRepoFilter: (name: string) => void;
}

export interface PromptsListComputedValues {
  filteredPrompts: Prompt[];
  totalPrompts: number;
  totalPages: number;
  paginatedPrompts: Prompt[];
}

export function useManagePromptsList(
  promptsState: PromptsState,
  updatePromptsState: PromptsStateUpdater
): {
  functions: PromptsListManagementFunctions;
  computed: PromptsListComputedValues;
} {
  // Search and pagination functions
  const setSearchQuery = useCallback((query: string) => {
    updatePromptsState(prev => ({
      ...prev,
      searchQuery: query,
      currentPage: 1 // Reset to first page when searching
    }));
  }, [updatePromptsState]);

  const setCurrentPage = useCallback((page: number) => {
    updatePromptsState(prev => ({ ...prev, currentPage: page }));
  }, [updatePromptsState]);

  const setSortBy = useCallback((sortBy: 'name' | 'updated_at', sortOrder: 'asc' | 'desc') => {
    updatePromptsState(prev => ({ ...prev, sortBy, sortOrder, currentPage: 1 }));
  }, [updatePromptsState]);

  const setRepoFilter = useCallback((name: string) => {
    updatePromptsState(prev => ({
      ...prev,
      repoFilter: name,
      currentPage: 1 // Reset to first page when filtering
    }));
  }, [updatePromptsState]);

  // Computed values for filtered, sorted, and paginated prompts
  const filteredPrompts = useMemo(() => {
    return promptsState.prompts.filter(prompt => {
      const matchesSearch = prompt.name.toLowerCase().includes(promptsState.searchQuery.toLowerCase()) ||
        prompt.description.toLowerCase().includes(promptsState.searchQuery.toLowerCase()) ||
        (prompt.repo?.name.toLowerCase().includes(promptsState.searchQuery.toLowerCase()) ?? false);

      const matchesRepo = !promptsState.repoFilter ||
        (prompt.repo?.name === promptsState.repoFilter);

      return matchesSearch && matchesRepo;
    });
  }, [promptsState.prompts, promptsState.searchQuery, promptsState.repoFilter]);

  const sortedPrompts = useMemo(() => {
    return [...filteredPrompts].sort((a, b) => {
      let comparison = 0;
      if (promptsState.sortBy === 'name') {
        comparison = a.name.localeCompare(b.name);
      } else {
        comparison = a.updated_at.getTime() - b.updated_at.getTime();
      }
      return promptsState.sortOrder === 'asc' ? comparison : -comparison;
    });
  }, [filteredPrompts, promptsState.sortBy, promptsState.sortOrder]);

  const totalPages = useMemo(() => {
    return Math.ceil(sortedPrompts.length / promptsState.itemsPerPage);
  }, [sortedPrompts, promptsState.itemsPerPage]);

  const startIndex = useMemo(() => {
    return (promptsState.currentPage - 1) * promptsState.itemsPerPage;
  }, [promptsState.currentPage, promptsState.itemsPerPage]);

  const paginatedPrompts = useMemo(() => {
    return sortedPrompts.slice(startIndex, startIndex + promptsState.itemsPerPage);
  }, [sortedPrompts, startIndex, promptsState.itemsPerPage]);

  return {
    functions: {
      setSearchQuery,
      setCurrentPage,
      setSortBy,
      setRepoFilter,
    },
    computed: {
      filteredPrompts,
      totalPrompts: sortedPrompts.length,
      totalPages,
      paginatedPrompts,
    },
  };
}