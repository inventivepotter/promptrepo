import { PromptStore } from './types';
import type { PromptMeta } from '@/services/prompts/api';

// Data Selectors - Convert Record to Array
export const selectPrompts = (state: PromptStore): PromptMeta[] =>
  Object.values(state.prompts);

export const selectCurrentPrompt = (state: PromptStore): PromptMeta | null => state.currentPrompt;

// Changed State Selector
export const selectIsChanged = (state: PromptStore): boolean => state.isChanged;

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
export const selectTotalPrompts = (state: PromptStore): number => {
  // Calculate total based on filtered prompts, not pagination.total
  const filtered = selectFilteredPrompts(state);
  return filtered.length;
};
export const selectTotalPages = (state: PromptStore): number => {
  // Calculate total pages based on filtered prompts, not pagination.totalPages
  const filtered = selectFilteredPrompts(state);
  return Math.ceil(filtered.length / state.pagination.pageSize);
};
export const selectHasNextPage = (state: PromptStore): boolean =>
  state.pagination.page < selectTotalPages(state);
export const selectHasPreviousPage = (state: PromptStore): boolean =>
  state.pagination.page > 1;

// Computed Selectors - Use object property access for efficient lookups
export const selectPromptByKey = (repoName: string, filePath: string) => (state: PromptStore): PromptMeta | undefined =>
  state.prompts[`${repoName}:${filePath}`];

export const selectPromptsByRepository = (repository: string) => (state: PromptStore): PromptMeta[] =>
  Object.values(state.prompts).filter(promptMeta => promptMeta.repo_name === repository);

// Create a selector that returns both the filtered prompts and the dependencies
export const selectFilteredPromptsData = (state: PromptStore) => ({
  prompts: state.prompts,
  search: state.filters.search,
  repository: state.filters.repository,
  sortBy: state.filters.sortBy,
  sortOrder: state.filters.sortOrder,
});

// The actual filtering function that processes the data
export const filterPrompts = (data: ReturnType<typeof selectFilteredPromptsData>): PromptMeta[] => {
  let filtered = Object.values(data.prompts);
  
  // Apply search filter
  if (data.search) {
    const searchLower = data.search.toLowerCase();
    filtered = filtered.filter(promptMeta => {
      const prompt = promptMeta.prompt;
      return (
        prompt.name.toLowerCase().includes(searchLower) ||
        prompt.prompt.toLowerCase().includes(searchLower) ||
        prompt.description?.toLowerCase().includes(searchLower)
      );
    });
  }
  
  // Apply repository filter
  if (data.repository) {
    filtered = filtered.filter(promptMeta => promptMeta.repo_name === data.repository);
  }
  
  // Apply sorting
  filtered.sort((a, b) => {
    const sortBy = data.sortBy || 'updated_at';
    const sortOrder = data.sortOrder || 'desc';
    
    // Guard against missing prompt property
    if (!a.prompt || !b.prompt) {
      return 0;
    }
    
    let comparison = 0;
    if (sortBy === 'name') {
      comparison = (a.prompt.name || '').localeCompare(b.prompt.name || '');
    } else if (sortBy === 'updated_at') {
      // Use updated_at if available, otherwise fall back to created_at, or use current time for proper sorting
      const aTime = a.prompt?.updated_at
        ? new Date(a.prompt.updated_at).getTime()
        : (a.prompt?.created_at ? new Date(a.prompt.created_at).getTime() : Date.now());
      const bTime = b.prompt?.updated_at
        ? new Date(b.prompt.updated_at).getTime()
        : (b.prompt?.created_at ? new Date(b.prompt.created_at).getTime() : Date.now());
      comparison = aTime - bTime;
    }
    
    return sortOrder === 'asc' ? comparison : -comparison;
  });
  
  return filtered;
};

// Backward compatibility selector
export const selectFilteredPrompts = (state: PromptStore): PromptMeta[] => {
  return filterPrompts(selectFilteredPromptsData(state));
};

export const selectPromptCount = (state: PromptStore): number => Object.keys(state.prompts).length;

export const selectIsEmpty = (state: PromptStore): boolean =>
  Object.keys(state.prompts).length === 0 && !state.isLoading;

// Frontend-only pagination selector that operates on filtered results
export const selectPaginatedPrompts = (state: PromptStore): PromptMeta[] => {
  const filtered = selectFilteredPrompts(state);
  const { page, pageSize } = state.pagination;
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  return filtered.slice(start, end);
};

export const selectPageInfo = (state: PromptStore) => {
  // Calculate pagination info based on filtered prompts
  const filtered = selectFilteredPrompts(state);
  const { page, pageSize } = state.pagination;
  const total = filtered.length;
  const totalPages = Math.ceil(total / pageSize);
  const start = total > 0 ? (page - 1) * pageSize + 1 : 0;
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

// Selector for unique repositories from loaded prompts
export const selectUniqueRepositories = (state: PromptStore): string[] => {
  const repos = new Set<string>();
  Object.values(state.prompts).forEach(promptMeta => {
    if (promptMeta.repo_name) {
      repos.add(promptMeta.repo_name);
    }
  });
  return Array.from(repos).sort();
};