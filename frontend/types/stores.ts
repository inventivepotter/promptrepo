// Store Types for Zustand State Management

// =============================================================================
// Auth Store Types
// =============================================================================

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  github?: {
    username: string;
    accessToken: string;
  };
}

export interface AuthState {
  // State
  user: AuthUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  sessionToken: string | null;
  error: string | null;
  
  // Actions
  oauthCallbackGithub: (code: string, state?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  updateUser: (updates: Partial<AuthUser>) => void;
  initializeAuth: () => Promise<void>;
  
  // Internal actions
  setLoading: (loading: boolean) => void;
  setUser: (user: AuthUser | null) => void;
  setSessionToken: (token: string | null) => void;
  setError: (error: string | null) => void;
}

// =============================================================================
// Prompts Store Types
// =============================================================================

export interface Prompt {
  id: string;
  name: string;
  content: string;
  description?: string;
  tags: string[];
  variables: PromptVariable[];
  createdAt: string;
  updatedAt: string;
  version: string;
  isArchived: boolean;
  metadata: PromptMetadata;
}

// Type alias for SearchFilters
export type SearchFilters = PromptSearchFilters;

export interface PromptVariable {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'array';
  description?: string;
  defaultValue?: unknown;
  required: boolean;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
}

export interface PromptMetadata {
  author?: string;
  estimatedTokens?: number;
  lastUsed?: string;
  usageCount?: number;
}

export interface PromptSearchFilters {
  query?: string;
  tags?: string[];
  dateRange?: {
    start: string;
    end: string;
    from?: Date;
    to?: Date;
  };
  isArchived?: boolean;
  archived?: boolean; // Alias for backward compatibility
}

export interface PromptState {
  // State
  prompts: Record<string, Prompt>;
  currentPrompt: Prompt | null;
  searchFilters: PromptSearchFilters;
  isLoading: boolean;
  error: string | null;
  
  // Computed
  filteredPrompts: Prompt[];
  promptTags: string[];
  
  // Actions
  loadPrompts: () => Promise<void>;
  createPrompt: (prompt: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>) => Promise<Prompt>;
  updatePrompt: (id: string, updates: Partial<Omit<Prompt, 'id'>>) => Promise<Prompt>;
  deletePrompt: (id: string) => Promise<void>;
  duplicatePrompt: (id: string) => Promise<Prompt>;
  archivePrompt: (id: string) => Promise<Prompt>;
  restorePrompt: (id: string) => Promise<Prompt>;
  
  // Selection and filtering
  setCurrentPrompt: (prompt: Prompt | null) => void;
  updateSearchFilters: (filters: Partial<PromptSearchFilters>) => void;
  clearFilters: () => void;
  applyFilters: () => void;
  
  // Computed properties
  getAllTags: () => string[];
  getAllCategories: () => string[];
  getPromptById: (id: string) => Prompt | null;
  
  // Internal actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

// =============================================================================
// API Response Types
// =============================================================================

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// =============================================================================
// Store Hook Types
// =============================================================================

export interface StoreSelectors<T> {
  useStore: () => T;
  useActions: () => Pick<T, {
    [K in keyof T]: T[K] extends (...args: never[]) => unknown ? K : never;
  }[keyof T]>;
  useState: () => Omit<T, {
    [K in keyof T]: T[K] extends (...args: never[]) => unknown ? K : never;
  }[keyof T]>;
}