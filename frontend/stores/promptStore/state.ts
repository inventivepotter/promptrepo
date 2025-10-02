// Initial state for Prompt Store
import type { PromptState } from './types';

export const initialPromptState: PromptState = {
  // Data - stored as Map for efficient lookups
  // Key format: "repo_name:file_path"
  prompts: new Map(),
  
  // Currently selected/editing prompt (serves as form data)
  currentPrompt: null,
  
  // UI State
  isLoading: false,
  isCreating: false,
  isUpdating: false,
  isDeleting: false,
  error: null,
  
  // Filters and Pagination (frontend-only)
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
  
  // Cache management
  lastSyncTimestamp: null,
};