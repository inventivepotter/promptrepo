// Combined prompt store actions
import type { StateCreator } from '@/lib/zustand';
import { promptsService } from '@/services/prompts/promptsService';
import type { Prompt, PromptCreate, PromptUpdate } from '@/types/Prompt';
import type { PromptStore, PromptActions, PromptFilters } from './types';

// Create all prompt actions as a single StateCreator
export const createPromptActions: StateCreator<PromptStore, [], [], PromptActions> = (set, get, api) => ({
  // CRUD Operations
  fetchPrompts: async (filters?: PromptFilters, page = 1, pageSize = 20) => {
    set((draft) => {
      draft.isLoading = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/fetch-start');

    try {
      // Call the service with backend-compatible parameters
      const result = await promptsService.getPrompts({
        query: filters?.search || get().filters.search || undefined,
        repo_name: filters?.repository || get().filters.repository || undefined,
        page,
        page_size: pageSize
      });
      
      // Handle the response from the service
      const { prompts, pagination } = result;
      
      set((draft) => {
        draft.prompts = prompts;
        draft.pagination = {
          page: pagination?.page || page,
          pageSize: pagination?.page_size || pageSize,
          total: pagination?.total_items || prompts.length,
          totalPages: pagination?.total_pages || Math.ceil(prompts.length / pageSize),
        };
        if (filters) {
          draft.filters = { ...draft.filters, ...filters };
        }
        draft.isLoading = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/fetch-success');
    } catch (error) {
      set((draft) => {
        draft.error = error instanceof Error ? error.message : 'Failed to fetch prompts';
        draft.isLoading = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/fetch-error');
    }
  },

  fetchPromptById: async (id: string) => {
    set((draft) => {
      draft.isLoading = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/fetch-by-id-start');

    try {
      const prompt = await promptsService.getPrompt(id);
      
      if (prompt) {
        set((draft) => {
          draft.currentPrompt = prompt;
          // Update in the list if exists
          const index = draft.prompts.findIndex(p => p.id === id);
          if (index !== -1) {
            draft.prompts[index] = prompt;
          }
          draft.isLoading = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'prompts/fetch-by-id-success');
      } else {
        throw new Error('Prompt not found');
      }
    } catch (error) {
      set((draft) => {
        draft.error = error instanceof Error ? error.message : 'Failed to fetch prompt';
        draft.isLoading = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/fetch-by-id-error');
    }
  },

  createPrompt: async (promptData: PromptCreate) => {
    set((draft) => {
      draft.isCreating = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/create-start');

    try {
      const newPrompt = await promptsService.createPrompt(promptData);
      
      set((draft) => {
        draft.prompts.unshift(newPrompt);
        draft.currentPrompt = newPrompt;
        draft.isCreating = false;
        draft.pagination.total += 1;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/create-success');
      
      return newPrompt;
    } catch (error) {
      set((draft) => {
        draft.error = error instanceof Error ? error.message : 'Failed to create prompt';
        draft.isCreating = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/create-error');
      throw error;
    }
  },

  updatePrompt: async (id: string, updates: PromptUpdate) => {
    const originalPrompt = get().prompts.find(p => p.id === id);
    
    // Optimistic update
    set((draft) => {
      draft.isUpdating = true;
      draft.error = null;
      
      if (originalPrompt) {
        draft.optimisticUpdates.set(id, originalPrompt);
        const index = draft.prompts.findIndex(p => p.id === id);
        if (index !== -1) {
          draft.prompts[index] = { ...draft.prompts[index], ...updates };
        }
        if (draft.currentPrompt?.id === id) {
          draft.currentPrompt = { ...draft.currentPrompt, ...updates };
        }
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/update-start');

    try {
      // Call the service with the correct parameters
      const updatedPrompt = await promptsService.updatePrompt(id, updates);
      
      set((draft) => {
        const index = draft.prompts.findIndex(p => p.id === id);
        if (index !== -1) {
          draft.prompts[index] = updatedPrompt;
        }
        if (draft.currentPrompt?.id === id) {
          draft.currentPrompt = updatedPrompt;
        }
        draft.optimisticUpdates.delete(id);
        draft.isUpdating = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/update-success');
    } catch (error) {
      // Rollback optimistic update
      set((draft) => {
        const original = draft.optimisticUpdates.get(id);
        if (original) {
          const index = draft.prompts.findIndex(p => p.id === id);
          if (index !== -1) {
            draft.prompts[index] = original;
          }
          if (draft.currentPrompt?.id === id) {
            draft.currentPrompt = original;
          }
          draft.optimisticUpdates.delete(id);
        }
        draft.error = error instanceof Error ? error.message : 'Failed to update prompt';
        draft.isUpdating = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/update-error');
      throw error;
    }
  },

  deletePrompt: async (id: string) => {
    const originalIndex = get().prompts.findIndex(p => p.id === id);
    const originalPrompt = get().prompts[originalIndex];
    
    // Optimistic delete
    set((draft) => {
      draft.isDeleting = true;
      draft.error = null;
      
      if (originalPrompt) {
        draft.optimisticUpdates.set(id, originalPrompt);
        draft.prompts.splice(originalIndex, 1);
        if (draft.currentPrompt?.id === id) {
          draft.currentPrompt = null;
        }
        draft.pagination.total -= 1;
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/delete-start');

    try {
      await promptsService.deletePrompt(id);
      
      set((draft) => {
        draft.optimisticUpdates.delete(id);
        draft.isDeleting = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/delete-success');
    } catch (error) {
      // Rollback optimistic delete
      set((draft) => {
        const original = draft.optimisticUpdates.get(id);
        if (original && originalIndex !== -1) {
          draft.prompts.splice(originalIndex, 0, original);
          draft.pagination.total += 1;
          draft.optimisticUpdates.delete(id);
        }
        draft.error = error instanceof Error ? error.message : 'Failed to delete prompt';
        draft.isDeleting = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'prompts/delete-error');
      throw error;
    }
  },

  // State Management
  setCurrentPrompt: (prompt: Prompt | null) => {
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

  // Filters and Search
  setFilters: (filters: PromptFilters) => {
    set((draft) => {
      draft.filters = { ...draft.filters, ...filters };
      draft.pagination.page = 1; // Reset to first page when filters change
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-filters');
    // Trigger fetch with new filters
    get().fetchPrompts(filters);
  },

  setSearch: (search: string) => {
    set((draft) => {
      draft.filters.search = search;
      draft.pagination.page = 1;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-search');
    get().fetchPrompts();
  },

  setRepository: (repository: string) => {
    set((draft) => {
      draft.filters.repository = repository;
      draft.pagination.page = 1;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-repository');
    get().fetchPrompts();
  },

  setSortBy: (sortBy: 'name' | 'updated_at') => {
    set((draft) => {
      draft.filters.sortBy = sortBy;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-sort-by');
    get().fetchPrompts();
  },

  setSortOrder: (sortOrder: 'asc' | 'desc') => {
    set((draft) => {
      draft.filters.sortOrder = sortOrder;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-sort-order');
    get().fetchPrompts();
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
    get().fetchPrompts();
  },

  // Pagination
  setPage: (page: number) => {
    set((draft) => {
      draft.pagination.page = page;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-page');
    get().fetchPrompts(undefined, page);
  },

  setPageSize: (pageSize: number) => {
    set((draft) => {
      draft.pagination.pageSize = pageSize;
      draft.pagination.page = 1; // Reset to first page when page size changes
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/set-page-size');
    get().fetchPrompts(undefined, 1, pageSize);
  },

  nextPage: () => {
    const { page, totalPages } = get().pagination;
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

  // Error Handling
  clearError: () => {
    set((draft) => {
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/clear-error');
  },

  // Reset
  reset: () => {
    set((draft) => {
      draft.prompts = [];
      draft.currentPrompt = null;
      draft.isLoading = false;
      draft.isCreating = false;
      draft.isUpdating = false;
      draft.isDeleting = false;
      draft.error = null;
      draft.filters = {
        search: '',
        repository: '',
        sortBy: 'updated_at',
        sortOrder: 'desc',
      };
      draft.pagination = {
        page: 1,
        pageSize: 20,
        total: 0,
        totalPages: 0,
      };
      draft.optimisticUpdates.clear();
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'prompts/reset');
  },
});