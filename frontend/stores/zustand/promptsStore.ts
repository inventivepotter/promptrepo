import { create } from 'zustand';
import { devtools, persist, immer, createLocalStorage } from '@/lib/zustand';
import type { PromptState, Prompt, SearchFilters } from '@/types/stores';

// =============================================================================
// Prompts Store Implementation
// =============================================================================

export const usePromptsStore = create<PromptState>()(
  devtools(
    persist(
      immer((set, get) => ({
        // Initial State
        prompts: {},
        currentPrompt: null,
        searchFilters: {
          query: '',
          tags: [],
          category: undefined,
          archived: false,
        },
        filteredPrompts: [],
        isLoading: false,
        error: null,
        
        // Actions
        loadPrompts: async () => {
          set((draft) => {
            draft.isLoading = true;
            draft.error = null;
          });
          
          try {
            const { promptsService } = await import('@/services/prompts/promptsService');
            const prompts = await promptsService.getPrompts();
            
            set((draft) => {
              draft.prompts = prompts.reduce((acc, prompt) => {
                acc[prompt.id] = prompt;
                return acc;
              }, {} as Record<string, Prompt>);
              draft.isLoading = false;
            });
            
            // Apply filters after loading
            get().applyFilters();
          } catch (error) {
            set((draft) => {
              draft.isLoading = false;
              draft.error = error instanceof Error ? error.message : 'Failed to load prompts';
            });
            throw error;
          }
        },
        
        createPrompt: async (prompt: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'>) => {
          set((draft) => {
            draft.isLoading = true;
            draft.error = null;
          });
          
          try {
            const { promptsService } = await import('@/services/prompts/promptsService');
            const newPrompt = await promptsService.createPrompt(prompt);
            
            set((draft) => {
              draft.prompts[newPrompt.id] = newPrompt;
              draft.currentPrompt = newPrompt;
              draft.isLoading = false;
            });
            
            // Re-apply filters
            get().applyFilters();
            
            return newPrompt;
          } catch (error) {
            set((draft) => {
              draft.isLoading = false;
              draft.error = error instanceof Error ? error.message : 'Failed to create prompt';
            });
            throw error;
          }
        },
        
        updatePrompt: async (id: string, updates: Partial<Omit<Prompt, 'id'>>) => {
          const prompt = get().prompts[id];
          if (!prompt) {
            throw new Error('Prompt not found');
          }
          
          set((draft) => {
            draft.isLoading = true;
            draft.error = null;
          });
          
          try {
            const { promptsService } = await import('@/services/prompts/promptsService');
            const updatedPrompt = await promptsService.updatePrompt(id, updates);
            
            set((draft) => {
              draft.prompts[id] = updatedPrompt;
              if (draft.currentPrompt?.id === id) {
                draft.currentPrompt = updatedPrompt;
              }
              draft.isLoading = false;
            });
            
            // Re-apply filters
            get().applyFilters();
            
            return updatedPrompt;
          } catch (error) {
            set((draft) => {
              draft.isLoading = false;
              draft.error = error instanceof Error ? error.message : 'Failed to update prompt';
            });
            throw error;
          }
        },
        
        deletePrompt: async (id: string) => {
          if (!get().prompts[id]) {
            throw new Error('Prompt not found');
          }
          
          set((draft) => {
            draft.isLoading = true;
            draft.error = null;
          });
          
          try {
            const { promptsService } = await import('@/services/prompts/promptsService');
            await promptsService.deletePrompt(id);
            
            set((draft) => {
              delete draft.prompts[id];
              if (draft.currentPrompt?.id === id) {
                draft.currentPrompt = null;
              }
              draft.isLoading = false;
            });
            
            // Re-apply filters
            get().applyFilters();
          } catch (error) {
            set((draft) => {
              draft.isLoading = false;
              draft.error = error instanceof Error ? error.message : 'Failed to delete prompt';
            });
            throw error;
          }
        },
        
        duplicatePrompt: async (id: string) => {
          const prompt = get().prompts[id];
          if (!prompt) {
            throw new Error('Prompt not found');
          }
          
          const duplicatedPrompt: Omit<Prompt, 'id' | 'createdAt' | 'updatedAt'> = {
            name: `${prompt.name} (Copy)`,
            content: prompt.content,
            description: prompt.description,
            tags: [...prompt.tags],
            variables: [...prompt.variables],
            version: '1.0.0',
            isArchived: false,
            metadata: { ...prompt.metadata },
          };
          
          return get().createPrompt(duplicatedPrompt);
        },
        
        archivePrompt: async (id: string) => {
          return get().updatePrompt(id, { isArchived: true });
        },
        
        restorePrompt: async (id: string) => {
          return get().updatePrompt(id, { isArchived: false });
        },
        
        setCurrentPrompt: (prompt: Prompt | null) => {
          set((draft) => {
            draft.currentPrompt = prompt;
          });
        },
        
        updateSearchFilters: (filters: Partial<SearchFilters>) => {
          set((draft) => {
            Object.assign(draft.searchFilters, filters);
          });
          
          // Apply filters immediately
          get().applyFilters();
        },
        
        clearFilters: () => {
          set((draft) => {
            draft.searchFilters = {
              query: '',
              tags: [],
              category: undefined,
              archived: false,
            };
          });
          
          // Apply filters immediately
          get().applyFilters();
        },
        
        applyFilters: () => {
          const { prompts, searchFilters } = get();
          const promptsList = Object.values(prompts);
          
          let filtered = promptsList;
          
          // Filter by archive status
          if (!searchFilters.archived) {
            filtered = filtered.filter(p => !p.isArchived);
          }
          
          // Filter by query (search in name, description, content)
          if (searchFilters.query) {
            const query = searchFilters.query.toLowerCase();
            filtered = filtered.filter(p => 
              p.name.toLowerCase().includes(query) ||
              p.description?.toLowerCase().includes(query) ||
              p.content.toLowerCase().includes(query)
            );
          }
          
          // Filter by tags
          if (searchFilters.tags && searchFilters.tags.length > 0) {
            filtered = filtered.filter(p => 
              searchFilters.tags!.some(tag => p.tags.includes(tag))
            );
          }
          
          // Filter by category
          if (searchFilters.category) {
            filtered = filtered.filter(p => 
              p.metadata.category === searchFilters.category
            );
          }
          
          // Filter by date range
          if (searchFilters.dateRange) {
            const { from, to } = searchFilters.dateRange;
            filtered = filtered.filter(p => {
              const createdAt = new Date(p.createdAt);
              return (!from || createdAt >= from) && (!to || createdAt <= to);
            });
          }
          
          // Sort by updatedAt (most recent first)
          filtered.sort((a, b) => 
            new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
          );
          
          set((draft) => {
            draft.filteredPrompts = filtered;
          });
        },
        
        // Computed properties
        getAllTags: () => {
          const { prompts } = get();
          const tagsSet = new Set<string>();
          Object.values(prompts).forEach(prompt => {
            prompt.tags.forEach(tag => tagsSet.add(tag));
          });
          return Array.from(tagsSet).sort();
        },
        
        getAllCategories: () => {
          const { prompts } = get();
          const categoriesSet = new Set<string>();
          Object.values(prompts).forEach(prompt => {
            if (prompt.metadata.category) {
              categoriesSet.add(prompt.metadata.category);
            }
          });
          return Array.from(categoriesSet).sort();
        },
        
        getPromptById: (id: string) => {
          return get().prompts[id] || null;
        },
        
        // Internal actions
        setLoading: (loading: boolean) => {
          set((draft) => {
            draft.isLoading = loading;
          });
        },
        
        setError: (error: string | null) => {
          set((draft) => {
            draft.error = error;
          });
        },
      })),
      {
        name: 'prompts-store',
        storage: createLocalStorage(),
        partialize: (state) => ({
          prompts: state.prompts,
          currentPrompt: state.currentPrompt,
          searchFilters: state.searchFilters,
        }),
      }
    ),
    {
      name: 'Prompts Store',
    }
  )
);

// =============================================================================
// Store Selectors
// =============================================================================

export const usePromptsActions = () => usePromptsStore((state) => ({
  loadPrompts: state.loadPrompts,
  createPrompt: state.createPrompt,
  updatePrompt: state.updatePrompt,
  deletePrompt: state.deletePrompt,
  duplicatePrompt: state.duplicatePrompt,
  archivePrompt: state.archivePrompt,
  restorePrompt: state.restorePrompt,
  setCurrentPrompt: state.setCurrentPrompt,
  updateSearchFilters: state.updateSearchFilters,
  clearFilters: state.clearFilters,
  applyFilters: state.applyFilters,
  setLoading: state.setLoading,
  setError: state.setError,
}));

export const usePromptsState = () => usePromptsStore((state) => ({
  prompts: state.prompts,
  currentPrompt: state.currentPrompt,
  searchFilters: state.searchFilters,
  filteredPrompts: state.filteredPrompts,
  isLoading: state.isLoading,
  error: state.error,
}));

export const usePrompts = () => usePromptsStore((state) => state.prompts);
export const useFilteredPrompts = () => usePromptsStore((state) => state.filteredPrompts);
export const useCurrentPrompt = () => usePromptsStore((state) => state.currentPrompt);
export const usePromptsLoading = () => usePromptsStore((state) => state.isLoading);
export const usePromptsError = () => usePromptsStore((state) => state.error);

// Computed selectors
export const useAllTags = () => usePromptsStore((state) => state.getAllTags());
export const useAllCategories = () => usePromptsStore((state) => state.getAllCategories());
export const usePromptById = (id: string) => usePromptsStore((state) => state.getPromptById(id));