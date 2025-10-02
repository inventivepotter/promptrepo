import { useMemo } from 'react';
import { usePromptStore } from './store';
import { useConfigStore } from '@/stores/configStore';
import {
  selectPrompts,
  selectCurrentPrompt,
  selectIsLoading,
  selectIsCreating,
  selectIsUpdating,
  selectIsDeleting,
  selectIsProcessing,
  selectError,
  selectFilters,
  selectSearch,
  selectRepository,
  selectSortBy,
  selectSortOrder,
  selectPagination,
  selectCurrentPage,
  selectPageSize,
  selectTotalPrompts,
  selectTotalPages,
  selectHasNextPage,
  selectHasPreviousPage,
  selectPromptByKey,
  selectPromptsByRepository,
  filterPrompts,
  selectPromptCount,
  selectIsEmpty,
  selectPageInfo,
} from './selectors';

// Data Hooks
export const usePrompts = () => usePromptStore(selectPrompts);
export const useCurrentPrompt = () => usePromptStore(selectCurrentPrompt);
export const usePromptByKey = (repoName: string, filePath: string) =>
  usePromptStore(selectPromptByKey(repoName, filePath));
export const usePromptsByRepository = (repository: string) =>
  usePromptStore(selectPromptsByRepository(repository));

// Fixed useFilteredPrompts hook with proper memoization
export const useFilteredPrompts = () => {
  // Select each piece of data separately for better memoization
  const prompts = usePromptStore(state => state.prompts);
  const search = usePromptStore(state => state.filters.search);
  const repository = usePromptStore(state => state.filters.repository);
  const sortBy = usePromptStore(state => state.filters.sortBy);
  const sortOrder = usePromptStore(state => state.filters.sortOrder);
  
  // Memoize the filtered result based on the individual dependencies
  return useMemo(() => {
    const filterData = {
      prompts,
      search,
      repository,
      sortBy,
      sortOrder,
    };
    return filterPrompts(filterData);
  }, [prompts, search, repository, sortBy, sortOrder]);
};

// Loading State Hooks
export const useIsLoading = () => usePromptStore(selectIsLoading);
export const useIsCreating = () => usePromptStore(selectIsCreating);
export const useIsUpdating = () => usePromptStore(selectIsUpdating);
export const useIsDeleting = () => usePromptStore(selectIsDeleting);
export const useIsProcessing = () => usePromptStore(selectIsProcessing);

// Error Hook
export const usePromptError = () => usePromptStore(selectError);

// Filter Hooks
export const usePromptFilters = () => usePromptStore(selectFilters);
export const usePromptSearch = () => usePromptStore(selectSearch);
export const usePromptRepository = () => usePromptStore(selectRepository);
export const usePromptSortBy = () => usePromptStore(selectSortBy);
export const usePromptSortOrder = () => usePromptStore(selectSortOrder);

// Pagination Hooks
export const usePromptPagination = () => usePromptStore(selectPagination);
export const useCurrentPage = () => usePromptStore(selectCurrentPage);
export const usePageSize = () => usePromptStore(selectPageSize);
export const useTotalPrompts = () => usePromptStore(selectTotalPrompts);
export const useTotalPages = () => usePromptStore(selectTotalPages);
export const useHasNextPage = () => usePromptStore(selectHasNextPage);
export const useHasPreviousPage = () => usePromptStore(selectHasPreviousPage);
export const usePageInfo = () => usePromptStore(selectPageInfo);

// Computed Hooks
export const useUniqueRepositories = () => {
  const prompts = usePromptStore(state => state.prompts);
  
  return useMemo(() => {
    const repositories = new Set<string>();
    Object.values(prompts).forEach(promptMeta => {
      if (promptMeta.repo_name) {
        repositories.add(promptMeta.repo_name);
      }
    });
    return Array.from(repositories).sort();
  }, [prompts]);
};

export const usePromptCount = () => usePromptStore(selectPromptCount);
export const useIsPromptsEmpty = () => usePromptStore(selectIsEmpty);

/**
 * Hook to get model options from config store
 * This provides provider/model options for UI components
 */
export const useModelOptions = () => {
  const config = useConfigStore(state => state.config);
  
  return useMemo(() => {
    const llmConfigs = config.llm_configs || [];
    return llmConfigs.map(llm => ({
      label: `${llm.provider} / ${llm.model}`,
      value: `${llm.provider}:${llm.model}`,
      provider: llm.provider,
      model: llm.model,
    }));
  }, [config.llm_configs]);
};

// Action Hooks
export const usePromptActions = () => {
  const store = usePromptStore();
  
  return {
    // Discovery & Sync
    discoverAllPromptsFromRepos: store.discoverAllPromptsFromRepos,
    initializeStore: store.initializeStore,
    
    // CRUD Operations
    fetchPrompts: store.fetchPrompts,
    fetchPromptById: store.fetchPromptById,
    createPrompt: store.createPrompt,
    updatePrompt: store.updatePrompt,
    deletePrompt: store.deletePrompt,
    
    // State Management
    setCurrentPrompt: store.setCurrentPrompt,
    clearCurrentPrompt: store.clearCurrentPrompt,
    
    // Convenience handlers
    saveCurrentPrompt: async () => {
      const currentPrompt = store.currentPrompt;
      if (currentPrompt) {
        // Use the entire currentPrompt.prompt as updates since it's already the modified state
        await store.updatePrompt(currentPrompt.repo_name, currentPrompt.file_path, currentPrompt.prompt);
      }
    },
    
    // Filters and Search
    setFilters: store.setFilters,
    setSearch: store.setSearch,
    setRepository: store.setRepository,
    setSortBy: store.setSortBy,
    setSortOrder: store.setSortOrder,
    clearFilters: store.clearFilters,
    
    // Pagination
    setPage: store.setPage,
    setPageSize: store.setPageSize,
    nextPage: store.nextPage,
    previousPage: store.previousPage,
    
    // Error Handling
    clearError: store.clearError,
  };
};

/**
 * Hook to update a single field in the current prompt
 * This provides a reusable pattern for field updates across components
 */
export const useUpdateCurrentPromptField = () => {
  const currentPrompt = useCurrentPrompt();
  const setCurrentPrompt = usePromptStore(state => state.setCurrentPrompt);

  return useMemo(() => {
    return (field: string, value: string | number | boolean | string[] | null | Record<string, unknown>) => {
      if (!currentPrompt) {
        return;
      }

      setCurrentPrompt({
        ...currentPrompt,
        prompt: {
          ...currentPrompt.prompt,
          [field]: value,
        },
      });
    };
  }, [currentPrompt, setCurrentPrompt]);
};

// Convenience hook that returns everything
export const usePromptStoreState = () => {
  const prompts = usePrompts();
  const currentPrompt = useCurrentPrompt();
  const isLoading = useIsLoading();
  const isCreating = useIsCreating();
  const isUpdating = useIsUpdating();
  const isDeleting = useIsDeleting();
  const isProcessing = useIsProcessing();
  const error = usePromptError();
  const filters = usePromptFilters();
  const pagination = usePromptPagination();
  const actions = usePromptActions();
  
  return {
    // Data
    prompts,
    currentPrompt,
    
    // Loading States
    isLoading,
    isCreating,
    isUpdating,
    isDeleting,
    isProcessing,
    
    // Error
    error,
    
    // Filters and Pagination
    filters,
    pagination,
    
    // Actions
    ...actions,
  };
};