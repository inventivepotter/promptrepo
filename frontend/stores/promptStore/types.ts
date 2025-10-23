import type { PromptMeta, PromptDataUpdate } from '@/services/prompts/api';

export interface PromptFilters {
  search?: string;
  repository?: string;
  sortBy?: 'name' | 'updated_at';
  sortOrder?: 'asc' | 'desc';
}

export interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
  totalPages: number;
}

export interface PromptState {
  // Data - stored as hashmap for efficient lookups
  // Key format: "repo_name:file_path"
  // Using Record instead of Map for better JSON serialization
  prompts: Record<string, PromptMeta>;
  
  // Currently selected/editing prompt (serves as form data)
  currentPrompt: PromptMeta | null;
  
  // Original prompt data for change tracking
  originalPrompt: PromptMeta | null;
  
  // UI State
  isLoading: boolean;
  isCreating: boolean;
  isUpdating: boolean;
  isDeleting: boolean;
  error: string | null;
  hasUnsavedChanges: boolean;
  
  // Delete dialog state
  deleteDialog: {
    isOpen: boolean;
    promptToDelete: { repoName: string; filePath: string; name: string } | null;
  };
  
  // Filters and Pagination (frontend-only)
  filters: PromptFilters;
  pagination: PaginationState;
  
  // Model selector UI state
  modelSearch: {
    primaryModel: string;
    failoverModel: string;
  };
  
  // Cache management
  lastSyncTimestamp: number | null;
}

export interface PromptActions {
  // Discovery & Sync
  discoverAllPromptsFromRepos: () => Promise<void>;
  
  // CRUD Operations
  fetchPrompts: (filters?: PromptFilters, page?: number, pageSize?: number) => Promise<void>;
  fetchPromptById: (repoName: string, filePath: string) => Promise<void>;
  createPrompt: (promptMeta: PromptMeta) => Promise<PromptMeta>;
  updatePrompt: (repoName: string, filePath: string, updates: PromptDataUpdate) => Promise<void>;
  deletePrompt: (repoName: string, filePath: string) => Promise<void>;
  
  initializeStore: () => Promise<void>;
  checkAndRefreshCache: () => Promise<void>;
  invalidateCache: () => void;
  
  // State Management
  setCurrentPrompt: (prompt: PromptMeta | null) => void;
  updateCurrentPrompt: (prompt: PromptMeta) => void;
  clearCurrentPrompt: () => void;
  checkForChanges: () => void;
  saveCurrentPrompt: () => Promise<void>;
  
  // Delete Dialog Management
  openDeleteDialog: (repoName: string, filePath: string, promptName: string) => void;
  closeDeleteDialog: () => void;
  confirmDelete: () => Promise<void>;
  
  // Filters and Search (frontend-only, no backend calls)
  setFilters: (filters: PromptFilters) => void;
  setSearch: (search: string) => void;
  setRepository: (repository: string) => void;
  setSortBy: (sortBy: 'name' | 'updated_at') => void;
  setSortOrder: (sortOrder: 'asc' | 'desc') => void;
  clearFilters: () => void;
  
  // Pagination (frontend-only)
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  nextPage: () => void;
  previousPage: () => void;
  
  // Model Search UI State
  setPrimaryModelSearch: (search: string) => void;
  setFailoverModelSearch: (search: string) => void;
  
  // Error Handling
  clearError: () => void;
}

export interface PromptStore extends PromptState, PromptActions {}