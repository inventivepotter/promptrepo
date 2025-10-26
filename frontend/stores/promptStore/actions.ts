// Combined prompt store actions
import type { StateCreator } from '@/lib/zustand';
import { promptsService } from '@/services/prompts/promptsService';
import ReposApi from '@/services/repos/api';
import { useConfigStore } from '@/stores/configStore/configStore';
import type { PromptStore, PromptActions, PromptFilters } from './types';
import type { PromptMeta, PromptDataUpdate } from '@/services/prompts/api';
import { del } from 'idb-keyval';

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
  
  // Invalidate cache - clear prompts and fetch fresh data
  invalidateCache: async () => {
    console.log('Prompt cache invalidated - clearing IndexedDB and resetting state');
    
    // Clear IndexedDB storage first to prevent rehydration
    try {
      if (typeof window !== 'undefined') {
        await del('prompt-store');
        console.log('Cleared prompt-store from IndexedDB');
      }
    } catch (err) {
      console.error('Failed to clear IndexedDB:', err);
    }
    
    // Clear in-memory state
    set((draft) => {
      draft.prompts = {};
      draft.lastSyncTimestamp = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/invalidate-cache');
    
    // Fetch fresh prompts from backend
    try {
      await get().discoverAllPromptsFromRepos();
    } catch (err) {
      console.error('Failed to refresh prompts after cache invalidation:', err);
    }
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
        console.warn('No repositories configured for discovery - clearing all prompts');
        set((draft) => {
          draft.prompts = {}; // Clear all prompts when no repos configured
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
        // Replace all prompts with fresh ones from discovery
        // This ensures we don't keep old prompts from repos that were removed
        const newPrompts: Record<string, PromptMeta> = {};
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
        draft.isChanged = false; // Reset isChanged when loading a prompt
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

  savePrompt: async (repoName: string, filePath: string, promptData: PromptDataUpdate) => {
    set((draft) => {
      draft.isUpdating = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/save-start');

    try {
      // If filePath is empty, generate it from prompt name
      let actualFilePath = filePath;
      if (!actualFilePath) {
        const promptName = promptData.name || 'untitled';
        let fileName = promptName
          .toLowerCase()
          .replace(/[^a-z0-9]+/g, '_')
          .replace(/^_+|_+$/g, '');
        // Guard against empty filename after sanitization
        if (!fileName) {
          fileName = 'untitled';
        }
        actualFilePath = `.promptrepo/prompts/${fileName}.prompt.yaml`;
      }

      const savedPromptMeta = await promptsService.savePrompt(repoName, actualFilePath, promptData);
      
      const promptKey = createPromptKey(savedPromptMeta.repo_name, savedPromptMeta.file_path);
      set((draft) => {
        draft.prompts[promptKey] = savedPromptMeta;
        if (draft.currentPrompt?.repo_name === repoName && draft.currentPrompt?.file_path === filePath) {
          draft.currentPrompt = savedPromptMeta;
        }
        draft.isChanged = false; // Reset isChanged after successful save
        draft.isUpdating = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/save-success');
      
      return savedPromptMeta;
    } catch (error) {
      set((draft) => {
        draft.error = error instanceof Error ? error.message : 'Failed to save prompt';
        draft.isUpdating = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/save-error');
      throw error;
    }
  },

  saveCurrentPrompt: async () => {
    const currentPrompt = get().currentPrompt;
    if (!currentPrompt) {
      throw new Error('No current prompt to save');
    }
    
    // Save the prompt - file path generation handled in savePrompt action
    const result = await get().savePrompt(
      currentPrompt.repo_name,
      currentPrompt.file_path || '', // Pass empty string if no file_path
      currentPrompt.prompt
    );
    return result;
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
      draft.isChanged = true; // Mark as changed when prompt is modified
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-current');
  },

  clearCurrentPrompt: () => {
    set((draft) => {
      draft.currentPrompt = null;
      draft.isChanged = false; // Reset isChanged when clearing
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

  // Get Latest from Base Branch
  getLatestFromBaseBranch: async (repoName: string) => {
    set((draft) => {
      draft.isLoading = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/get-latest-start');

    try {
      const result = await ReposApi.getLatestFromBaseBranch(repoName);
      
      // Check for backend soft failures
      const responseData = result as { data?: { status?: string; data?: { success?: boolean; message?: string | undefined } } };
      const status = responseData?.data?.status;
      const op = responseData?.data?.data; // service dict
      if (status !== 'success' || op?.success === false) {
        throw new Error(op?.message || responseData?.data?.data?.message || 'Get latest failed');
      }

      // Fully invalidate persisted + memory cache
      await get().invalidateCache();

      // If there's a current prompt open from the same repo, reload it to get the latest version
      const currentPrompt = get().currentPrompt;
      if (currentPrompt && currentPrompt.repo_name === repoName) {
        try {
          await get().fetchPromptById(currentPrompt.repo_name, currentPrompt.file_path);
        } catch {
          // If the file moved/deleted upstream, redirect to prompts page
          // Note: Can't use useRouter in store action, use window.location instead
          if (typeof window !== 'undefined') {
            window.location.href = '/prompts';
          }
        }
      }
      
      return result;
    } catch (error) {
      set((draft) => {
        draft.isLoading = false;
        draft.error = error instanceof Error ? error.message : 'Failed to get latest from base branch';
        // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/get-latest-error');
      throw error;
    }
  },

});