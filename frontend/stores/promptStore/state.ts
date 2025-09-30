// Initial state for Prompt Store
import type { PromptState } from './types';

export const initialPromptState: PromptState = {
  // Data
  prompts: [],
  currentPrompt: null,
  
  // UI State
  isLoading: false,
  isCreating: false,
  isUpdating: false,
  isDeleting: false,
  error: null,
  
  // Filters and Pagination
  filters: {
    search: '',
    repository: '',
    sortBy: 'updated_at',
    sortOrder: 'desc',
  },
  pagination: {
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0,
  },
  
  // Optimistic update tracking
  optimisticUpdates: new Map(),
};