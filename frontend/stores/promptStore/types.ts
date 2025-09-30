import { Prompt } from '@/types/Prompt';

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
  // Data
  prompts: Prompt[];
  currentPrompt: Prompt | null;
  
  // UI State
  isLoading: boolean;
  isCreating: boolean;
  isUpdating: boolean;
  isDeleting: boolean;
  error: string | null;
  
  // Filters and Pagination
  filters: PromptFilters;
  pagination: PaginationState;
  
  // Optimistic update tracking
  optimisticUpdates: Map<string, Prompt>;
}

export interface PromptActions {
  // CRUD Operations
  fetchPrompts: (filters?: PromptFilters, page?: number, pageSize?: number) => Promise<void>;
  fetchPromptById: (id: string) => Promise<void>;
  createPrompt: (prompt: Omit<Prompt, 'id' | 'created_at' | 'updated_at'>) => Promise<Prompt>;
  updatePrompt: (id: string, updates: Partial<Prompt>) => Promise<void>;
  deletePrompt: (id: string) => Promise<void>;
  
  // State Management
  setCurrentPrompt: (prompt: Prompt | null) => void;
  clearCurrentPrompt: () => void;
  
  // Filters and Search
  setFilters: (filters: PromptFilters) => void;
  setSearch: (search: string) => void;
  setRepository: (repository: string) => void;
  setSortBy: (sortBy: 'name' | 'updated_at') => void;
  setSortOrder: (sortOrder: 'asc' | 'desc') => void;
  clearFilters: () => void;
  
  // Pagination
  setPage: (page: number) => void;
  setPageSize: (pageSize: number) => void;
  nextPage: () => void;
  previousPage: () => void;
  
  // Error Handling
  clearError: () => void;
  
  // Reset
  reset: () => void;
}

export interface PromptStore extends PromptState, PromptActions {}