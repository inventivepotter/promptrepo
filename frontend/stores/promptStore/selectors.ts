import { PromptStore } from './types';
import { Prompt } from '@/types/Prompt';

// Data Selectors
export const selectPrompts = (state: PromptStore): Prompt[] => state.prompts;
export const selectCurrentPrompt = (state: PromptStore): Prompt | null => state.currentPrompt;

// Loading State Selectors
export const selectIsLoading = (state: PromptStore): boolean => state.isLoading;
export const selectIsCreating = (state: PromptStore): boolean => state.isCreating;
export const selectIsUpdating = (state: PromptStore): boolean => state.isUpdating;
export const selectIsDeleting = (state: PromptStore): boolean => state.isDeleting;
export const selectIsProcessing = (state: PromptStore): boolean =>
  state.isLoading || state.isCreating || state.isUpdating || state.isDeleting;

// Error Selector
export const selectError = (state: PromptStore): string | null => state.error;

// Filter Selectors
export const selectFilters = (state: PromptStore) => state.filters;
export const selectSearch = (state: PromptStore): string => state.filters.search || '';
export const selectRepository = (state: PromptStore): string => state.filters.repository || '';
export const selectSortBy = (state: PromptStore) => state.filters.sortBy;
export const selectSortOrder = (state: PromptStore) => state.filters.sortOrder;

// Pagination Selectors
export const selectPagination = (state: PromptStore) => state.pagination;
export const selectCurrentPage = (state: PromptStore): number => state.pagination.page;
export const selectPageSize = (state: PromptStore): number => state.pagination.pageSize;
export const selectTotalPrompts = (state: PromptStore): number => state.pagination.total;
export const selectTotalPages = (state: PromptStore): number => state.pagination.totalPages;
export const selectHasNextPage = (state: PromptStore): boolean =>
  state.pagination.page < state.pagination.totalPages;
export const selectHasPreviousPage = (state: PromptStore): boolean =>
  state.pagination.page > 1;

// Computed Selectors
export const selectPromptById = (id: string) => (state: PromptStore): Prompt | undefined =>
  state.prompts.find(prompt => prompt.id === id);

export const selectPromptsByRepository = (repository: string) => (state: PromptStore): Prompt[] =>
  state.prompts.filter(prompt => prompt.repo?.name === repository);

// Create a selector that returns both the filtered prompts and the dependencies
// This allows Zustand to properly memoize based on the actual dependencies
export const selectFilteredPromptsData = (state: PromptStore) => ({
  prompts: state.prompts,
  search: state.filters.search,
  repository: state.filters.repository,
  sortBy: state.filters.sortBy,
  sortOrder: state.filters.sortOrder,
});

// The actual filtering function that processes the data
export const filterPrompts = (data: ReturnType<typeof selectFilteredPromptsData>): Prompt[] => {
  let filtered = [...data.prompts];
  
  // Apply search filter
  if (data.search) {
    const searchLower = data.search.toLowerCase();
    filtered = filtered.filter(prompt =>
      prompt.name.toLowerCase().includes(searchLower) ||
      prompt.content.toLowerCase().includes(searchLower) ||
      prompt.description?.toLowerCase().includes(searchLower) ||
      prompt.system_prompt?.toLowerCase().includes(searchLower) ||
      prompt.user_prompt?.toLowerCase().includes(searchLower)
    );
  }
  
  // Apply repository filter
  if (data.repository) {
    filtered = filtered.filter(prompt => prompt.repo?.name === data.repository);
  }
  
  // Apply sorting
  filtered.sort((a, b) => {
    const sortBy = data.sortBy || 'updated_at';
    const sortOrder = data.sortOrder || 'desc';
    
    let comparison = 0;
    if (sortBy === 'name') {
      comparison = a.name.localeCompare(b.name);
    } else if (sortBy === 'updated_at') {
      comparison = new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime();
    }
    
    return sortOrder === 'asc' ? comparison : -comparison;
  });
  
  return filtered;
};

// Backward compatibility selector
export const selectFilteredPrompts = (state: PromptStore): Prompt[] => {
  return filterPrompts(selectFilteredPromptsData(state));
};

export const selectPromptCount = (state: PromptStore): number => state.prompts.length;

export const selectIsEmpty = (state: PromptStore): boolean => 
  state.prompts.length === 0 && !state.isLoading;

export const selectPageInfo = (state: PromptStore) => {
  const { page, pageSize, total, totalPages } = state.pagination;
  const start = (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, total);
  
  return {
    start,
    end,
    total,
    currentPage: page,
    totalPages,
    pageSize,
  };
};