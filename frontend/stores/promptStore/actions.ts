// Combined prompt store actions
import type { StateCreator } from '@/lib/zustand';
import { promptsService } from '@/services/prompts/promptsService';
import { useConfigStore } from '@/stores/configStore/configStore';
import type { PromptStore, PromptActions, PromptFilters } from './types';
import type { PromptMeta, PromptDataUpdate } from '@/services/prompts/api';

// Helper function to create consistent Map keys
const createPromptKey = (repoName: string, filePath: string): string =>
  `${repoName}:${filePath}`;

const CACHE_DURATION = 1000 * 60 * 60; // 1 hour in milliseconds

// Helper to check if cache is stale
const isCacheStale = (lastSyncTimestamp: number | null): boolean => {
  if (!lastSyncTimestamp) return true;
  const age = Date.now() - lastSyncTimestamp;
  return age >= CACHE_DURATION;
};

// Create all prompt actions as a single StateCreator
export const createPromptActions: StateCreator<PromptStore, [], [], PromptActions> = (set, get, api) => ({
  // Initialize store - check cache and auto-sync if needed
  initializeStore: async () => {
    const state = get();
    
    // If we have cached data and it's not stale, we're done
    const promptCount = Object.keys(state.prompts).length;
    if (promptCount > 0 && !isCacheStale(state.lastSyncTimestamp)) {
      const age = state.lastSyncTimestamp ? Date.now() - state.lastSyncTimestamp : 0;
      console.log('Using cached prompts, age:', Math.round(age / 1000), 'seconds');
      return;
    }
    
    // Cache is empty or stale, trigger auto-sync
    console.log('Cache empty or stale, triggering auto-sync');
    await get().discoverAllPromptsFromRepos();
  },
  
  // Check cache staleness and refresh if needed
  checkAndRefreshCache: async () => {
    const state = get();
    
    // If cache is stale, refresh
    if (isCacheStale(state.lastSyncTimestamp)) {
      console.log('Cache is stale, refreshing...');
      await get().discoverAllPromptsFromRepos();
    }
  },
  
  // Invalidate cache - clear prompts and force refresh on next access
  invalidateCache: () => {
    set((draft) => {
      draft.prompts = {};
      draft.lastSyncTimestamp = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/invalidate-cache');
    console.log('Prompt cache invalidated');
  },

  // Discover prompts from all configured repositories
  discoverAllPromptsFromRepos: async () => {
    set((draft) => {
      draft.isLoading = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/discover-all-start');

    try {
      // Get configured repositories from config store (uses cached data if available)
      const configState = useConfigStore.getState();
      const repoConfigs = configState.config?.repo_configs || [];
      
      if (repoConfigs.length === 0) {
        console.warn('No repositories configured for discovery');
        set((draft) => {
          draft.isLoading = false;
          draft.lastSyncTimestamp = Date.now();
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'prompts/discover-all-no-repos');
        return;
      }

      // Extract repo names from config
      const repoNames = repoConfigs.map(rc => rc.repo_name);
      
      // Discover prompts from all repositories
      const allPrompts = await promptsService.discoverAllPromptsFromRepos(repoNames);

      set((draft) => {
        // Merge discovered prompts with existing ones instead of replacing
        // This prevents losing prompts that were just created
        const newPrompts: Record<string, PromptMeta> = { ...draft.prompts };
        allPrompts.forEach((promptMeta: PromptMeta) => {
          const key = createPromptKey(promptMeta.repo_name, promptMeta.file_path);
          newPrompts[key] = promptMeta;
        });
        draft.prompts = newPrompts;
        draft.lastSyncTimestamp = Date.now();
        draft.isLoading = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/discover-all-success');
    } catch (error) {
      set((draft) => {
        draft.error = error instanceof Error ? error.message : 'Failed to discover repositories';
        draft.isLoading = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/discover-all-error');
    }
  },

  // CRUD Operations - updated to work with cached data
  fetchPrompts: async () => {
    // Check if we need to initialize
    const state = get();
    if (Object.keys(state.prompts).length === 0) {
      await get().initializeStore();
    }
    
    // No backend call needed - filtering and pagination are done via selectors
  },

  fetchPromptById: async (repoName: string, filePath: string) => {
    set((draft) => {
      draft.isLoading = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/fetch-by-id-start');

    try {
      const promptMeta = await promptsService.getPrompt(repoName, filePath);
      
      if (!promptMeta) {
        throw new Error('Prompt not found');
      }

      const key = createPromptKey(repoName, filePath);
      set((draft) => {
        draft.currentPrompt = promptMeta;
        draft.prompts[key] = promptMeta;
        draft.isLoading = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/fetch-by-id-success');
    } catch (error) {
      set((draft) => {
        draft.error = error instanceof Error ? error.message : 'Failed to fetch prompt';
        draft.isLoading = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/fetch-by-id-error');
      throw error;
    }
  },

  createPrompt: async (promptMeta: PromptMeta) => {
    set((draft) => {
      draft.isCreating = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/create-start');

    try {
      const newPromptMeta = await promptsService.createPrompt(promptMeta);
      
      const key = createPromptKey(newPromptMeta.repo_name, newPromptMeta.file_path);
      set((draft) => {
        draft.prompts[key] = newPromptMeta;
        draft.currentPrompt = newPromptMeta;
        draft.isCreating = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/create-success');
      
      return newPromptMeta;
    } catch (error) {
      set((draft) => {
        draft.error = error instanceof Error ? error.message : 'Failed to create prompt';
        draft.isCreating = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/create-error');
      throw error;
    }
  },

  updatePrompt: async (repoName: string, filePath: string, updates: PromptDataUpdate) => {
    set((draft) => {
      draft.isUpdating = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/update-start');

    try {
      const updatedPromptMeta = await promptsService.updatePrompt(repoName, filePath, updates);
      
      const promptKey = createPromptKey(repoName, filePath);
      set((draft) => {
        draft.prompts[promptKey] = updatedPromptMeta;
        if (draft.currentPrompt?.repo_name === repoName && draft.currentPrompt?.file_path === filePath) {
          draft.currentPrompt = updatedPromptMeta;
        }
        draft.isUpdating = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/update-success');
    } catch (error) {
      set((draft) => {
        draft.error = error instanceof Error ? error.message : 'Failed to update prompt';
        draft.isUpdating = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/update-error');
      throw error;
    }
  },

  deletePrompt: async (repoName: string, filePath: string) => {
    set((draft) => {
      draft.isDeleting = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/delete-start');

    try {
      await promptsService.deletePrompt(repoName, filePath);
      
      const promptKey = createPromptKey(repoName, filePath);
      set((draft) => {
        delete draft.prompts[promptKey];
        if (draft.currentPrompt?.repo_name === repoName && draft.currentPrompt?.file_path === filePath) {
          draft.currentPrompt = null;
        }
        draft.isDeleting = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/delete-success');
    } catch (error) {
      set((draft) => {
        draft.error = error instanceof Error ? error.message : 'Failed to delete prompt';
        draft.isDeleting = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/delete-error');
      throw error;
    }
  },

  // State Management
  setCurrentPrompt: (prompt: PromptMeta | null) => {
    set((draft) => {
      draft.currentPrompt = prompt;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-current');
  },

  clearCurrentPrompt: () => {
    set((draft) => {
      draft.currentPrompt = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/clear-current');
  },

  // Delete Dialog Management
  openDeleteDialog: (repoName: string, filePath: string, promptName: string) => {
    set((draft) => {
      draft.deleteDialog = {
        isOpen: true,
        promptToDelete: { repoName, filePath, name: promptName },
      };
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/open-delete-dialog');
  },

  closeDeleteDialog: () => {
    set((draft) => {
      draft.deleteDialog = {
        isOpen: false,
        promptToDelete: null,
      };
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/close-delete-dialog');
  },

  confirmDelete: async () => {
    const { deleteDialog } = get();
    const promptToDelete = deleteDialog.promptToDelete;
    
    if (!promptToDelete) return;

    try {
      await get().deletePrompt(promptToDelete.repoName, promptToDelete.filePath);
      get().closeDeleteDialog();
    } catch (error) {
      // Error is already handled by deletePrompt
      throw error;
    }
  },

  // Filters and Search - frontend-only, no backend calls
  setFilters: (filters: PromptFilters) => {
    set((draft) => {
      draft.filters = { ...draft.filters, ...filters };
      draft.pagination.page = 1; // Reset to first page when filters change
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-filters');
  },

  setSearch: (search: string) => {
    set((draft) => {
      draft.filters.search = search;
      draft.pagination.page = 1;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-search');
  },

  setRepository: (repository: string) => {
    set((draft) => {
      draft.filters.repository = repository;
      draft.pagination.page = 1;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-repository');
  },

  setSortBy: (sortBy: 'name' | 'updated_at') => {
    set((draft) => {
      draft.filters.sortBy = sortBy;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-sort-by');
  },

  setSortOrder: (sortOrder: 'asc' | 'desc') => {
    set((draft) => {
      draft.filters.sortOrder = sortOrder;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-sort-order');
  },

  clearFilters: () => {
    set((draft) => {
      draft.filters = {
        search: '',
        repository: '',
        sortBy: 'updated_at',
        sortOrder: 'desc',
      };
      draft.pagination.page = 1;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/clear-filters');
  },

  // Pagination - frontend-only
  setPage: (page: number) => {
    set((draft) => {
      draft.pagination.page = page;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-page');
  },

  setPageSize: (pageSize: number) => {
    set((draft) => {
      draft.pagination.pageSize = pageSize;
      draft.pagination.page = 1; // Reset to first page when page size changes
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-page-size');
  },

  nextPage: () => {
    const state = get();
    // Use selectPageInfo to get correct totalPages from filtered results
    const { totalPages, page } = state.pagination;
    if (page < totalPages) {
      get().setPage(page + 1);
    }
  },

  previousPage: () => {
    const { page } = get().pagination;
    if (page > 1) {
      get().setPage(page - 1);
    }
  },

  // Model Search UI State
  setPrimaryModelSearch: (search: string) => {
    set((draft) => {
      draft.modelSearch.primaryModel = search;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-primary-model-search');
  },

  setFailoverModelSearch: (search: string) => {
    set((draft) => {
      draft.modelSearch.failoverModel = search;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-failover-model-search');
  },

  // Error Handling
  clearError: () => {
    set((draft) => {
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/clear-error');
  },

});