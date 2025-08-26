import { useState, useRef, useEffect, useCallback } from "react";
import { getPromptsFromPersistance } from '../_lib/getPromptsFromPersistance';
import { getConfiguredRepos } from '../_lib/getConfiguredRepos';
import { PromptsState } from '../_types/state';
import { Prompt } from '@/types/Prompt';
import { LOCAL_STORAGE_KEYS } from '../_lib/localStorageConstants';

// Re-export types for backward compatibility
export type { PromptsState } from '../_types/state';

const defaultPrompt: Omit<Prompt, 'id' | 'created_at' | 'updated_at'> = {
  name: "",
  description: "",
  prompt: "",
  model: "",
  failover_model: "",
  temperature: 0.7,
  top_p: 1.0,
  max_tokens: 2048,
  thinking_enabled: false,
  thinking_budget: 20000,
};

const defaultPromptsState: PromptsState = {
  prompts: [],
  currentPrompt: null,
  searchQuery: "",
  currentPage: 1,
  itemsPerPage: 9,
  sortBy: 'updated_at',
  sortOrder: 'desc',
  configuredRepos: [],
  repoFilter: "",
  currentRepoStep: {
    isLoggedIn: false,
    selectedRepo: "",
    selectedBranch: "",
  },
};

// Persistence helper
const persistPrompts = (prompts: Prompt[]) => {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(LOCAL_STORAGE_KEYS.PROMPTS_DATA, JSON.stringify(prompts));
  }
};

// Cache selected repos to localStorage for fallback (primary source is now API via getConfiguredRepos)
const persistSelectedRepos = (configuredRepos: PromptsState['configuredRepos']) => {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(LOCAL_STORAGE_KEYS.CONFIGURED_REPOS, JSON.stringify(configuredRepos));
  }
};

// Load configured repos from localStorage with API fallback
const loadSelectedRepos = async (): Promise<PromptsState['configuredRepos']> => {
  try {
    // First check localStorage for existing configured repos
    if (typeof window !== "undefined") {
      const saved = window.localStorage.getItem(LOCAL_STORAGE_KEYS.CONFIGURED_REPOS);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          // Validate that we have an array of repos
          if (Array.isArray(parsed) && parsed.length > 0) {
            return parsed;
          }
        } catch (parseError) {
          console.error("Failed to parse selected repos from localStorage:", parseError);
        }
      }
    }
    
    // If no valid data in localStorage, try to get from API
    const configuredRepos = await getConfiguredRepos();
    
    // Update localStorage cache with fresh API data
    if (typeof window !== "undefined" && configuredRepos.length > 0) {
      window.localStorage.setItem(LOCAL_STORAGE_KEYS.CONFIGURED_REPOS, JSON.stringify(configuredRepos));
    }
    return configuredRepos;
  } catch (error) {
    console.error("Failed to load configured repos from API, falling back to localStorage:", error);
    
    // Fallback to localStorage if API call fails
    if (typeof window !== "undefined") {
      const saved = window.localStorage.getItem(LOCAL_STORAGE_KEYS.CONFIGURED_REPOS);
      if (saved) {
        try {
          return JSON.parse(saved);
        } catch (parseError) {
          console.error("Failed to parse selected repos from localStorage:", parseError);
        }
      }
    }
    return [];
  }
};

export function usePromptsState() {
  const [promptsState, setPromptsState] = useState<PromptsState>(defaultPromptsState);
  const hasRestoredData = useRef(false);

  useEffect(() => {
    if (!hasRestoredData.current && typeof window !== "undefined") {
      // Initialize data loading
      const initializeData = async () => {
        try {
          // Load configured repos from API
          const configuredRepos = await loadSelectedRepos();
          
          // Load prompts from localStorage
          const saved = window.localStorage.getItem(LOCAL_STORAGE_KEYS.PROMPTS_DATA);
          if (saved) {
            try {
              const parsed = JSON.parse(saved);
              if (Array.isArray(parsed)) {
                // Convert date strings back to Date objects
                const prompts = parsed.map(p => ({
                  ...p,
                  created_at: new Date(p.created_at),
                  updated_at: new Date(p.updated_at),
                }));
                // Merge new prompts from getPrompts if not already present
                const mockPrompts = getPromptsFromPersistance();
                const mergedPrompts = [
                  ...prompts,
                  ...mockPrompts.filter(
                    mp => !prompts.some(p => p.id === mp.id)
                  ),
                ];
                setPromptsState(prev => ({
                  ...prev,
                  prompts: mergedPrompts,
                  configuredRepos: configuredRepos // Use repos from API
                }));
                persistPrompts(mergedPrompts);
              }
            } catch (error) {
              console.error("Failed to restore prompts data:", error);
            }
          } else {
            // If nothing in localStorage, insert all from getPrompts
            const mockPrompts = getPromptsFromPersistance();
            setPromptsState(prev => ({
              ...prev,
              prompts: mockPrompts,
              configuredRepos: configuredRepos // Use repos from API
            }));
            persistPrompts(mockPrompts);
          }
        } catch (error) {
          console.error("Failed to initialize data:", error);
          // Continue with default empty configuredRepos if everything fails
          const mockPrompts = getPromptsFromPersistance();
          setPromptsState(prev => ({
            ...prev,
            prompts: mockPrompts,
            configuredRepos: []
          }));
          persistPrompts(mockPrompts);
        }
      };
      
      initializeData();
      hasRestoredData.current = true;
    }
  }, []);

  const updatePromptsState = useCallback((updater: PromptsState | ((prev: PromptsState) => PromptsState), shouldPersist: boolean = false) => {
    setPromptsState(prev => {
      const newState = typeof updater === 'function' ? updater(prev) : updater;
      // Only persist prompts when explicitly requested (e.g., on save)
      if (shouldPersist) {
        persistPrompts(newState.prompts);
      }
      return newState;
    });
  }, []);

  const createPrompt = useCallback(() => {
    const newPrompt: Prompt = {
      ...defaultPrompt,
      id: `prompt_${Date.now()}_${Math.random().toString(36).substring(2)}`,
      created_at: new Date(),
      updated_at: new Date(),
    };
    
    updatePromptsState(prev => ({
      ...prev,
      prompts: [newPrompt, ...prev.prompts],
      currentPrompt: newPrompt,
    }), true); // Persist when creating new prompt
    
    return newPrompt;
  }, [updatePromptsState]);

  const updatePrompt = useCallback((id: string, updates: Partial<Omit<Prompt, 'id' | 'created_at' | 'updated_at'>>, shouldPersist: boolean = true) => {
    updatePromptsState(prev => ({
      ...prev,
      prompts: prev.prompts.map(prompt =>
        prompt.id === id
          ? { ...prompt, ...updates, updated_at: new Date() }
          : prompt
      ),
      currentPrompt: prev.currentPrompt?.id === id
        ? { ...prev.currentPrompt, ...updates, updated_at: new Date() }
        : prev.currentPrompt,
    }), shouldPersist);
  }, [updatePromptsState]);

  const deletePrompt = useCallback((id: string) => {
    updatePromptsState(prev => ({
      ...prev,
      prompts: prev.prompts.filter(prompt => prompt.id !== id),
      currentPrompt: prev.currentPrompt?.id === id ? null : prev.currentPrompt,
    }), true); // Persist when deleting prompt
  }, [updatePromptsState]);

  const setCurrentPrompt = useCallback((prompt: Prompt | null) => {
    updatePromptsState(prev => ({ ...prev, currentPrompt: prompt }));
  }, [updatePromptsState]);

  const setSearchQuery = useCallback((query: string) => {
    updatePromptsState(prev => ({ 
      ...prev, 
      searchQuery: query,
      currentPage: 1 // Reset to first page when searching
    }));
  }, [updatePromptsState]);

  const setCurrentPage = useCallback((page: number) => {
    updatePromptsState(prev => ({ ...prev, currentPage: page }));
  }, [updatePromptsState]);

  const setSortBy = useCallback((sortBy: 'name' | 'updated_at', sortOrder: 'asc' | 'desc') => {
    updatePromptsState(prev => ({ ...prev, sortBy, sortOrder, currentPage: 1 }));
  }, [updatePromptsState]);

  // Filtered and sorted prompts
  const filteredPrompts = promptsState.prompts.filter(prompt => {
    const matchesSearch = prompt.name.toLowerCase().includes(promptsState.searchQuery.toLowerCase()) ||
      prompt.description.toLowerCase().includes(promptsState.searchQuery.toLowerCase()) ||
      (prompt.repo?.name.toLowerCase().includes(promptsState.searchQuery.toLowerCase()) ?? false);
    
    const matchesRepo = !promptsState.repoFilter ||
      (prompt.repo?.name === promptsState.repoFilter);
    
    return matchesSearch && matchesRepo;
  });

  const sortedPrompts = [...filteredPrompts].sort((a, b) => {
    let comparison = 0;
    if (promptsState.sortBy === 'name') {
      comparison = a.name.localeCompare(b.name);
    } else {
      comparison = a.updated_at.getTime() - b.updated_at.getTime();
    }
    return promptsState.sortOrder === 'asc' ? comparison : -comparison;
  });

  // Paginated prompts
  const totalPages = Math.ceil(sortedPrompts.length / promptsState.itemsPerPage);
  const startIndex = (promptsState.currentPage - 1) * promptsState.itemsPerPage;
  const paginatedPrompts = sortedPrompts.slice(startIndex, startIndex + promptsState.itemsPerPage);

  // Repo management functions
  const setRepoFilter = useCallback((name: string) => {
    updatePromptsState(prev => ({
      ...prev,
      repoFilter: name,
      currentPage: 1 // Reset to first page when filtering
    }));
  }, [updatePromptsState]);

  const updateCurrentRepoStepField = useCallback((field: keyof PromptsState['currentRepoStep'], value: string | boolean) => {
    updatePromptsState(prev => ({
      ...prev,
      currentRepoStep: { ...prev.currentRepoStep, [field]: value }
    }));
  }, [updatePromptsState]);

  const toggleRepoSelection = useCallback((id: string, base_branch: string, name: string) => {
    updatePromptsState(prev => {
      const existingIndex = prev.configuredRepos.findIndex(r => r.id === id);
      let newSelectedRepos;
      
      if (existingIndex >= 0) {
        const existing = prev.configuredRepos[existingIndex];
        if (existing.base_branch === base_branch) {
          newSelectedRepos = prev.configuredRepos.filter(r => r.id !== id);
        } else {
          newSelectedRepos = prev.configuredRepos.map((r, i) =>
            i === existingIndex ? { ...r, base_branch: base_branch } : r
          );
        }
      } else {
        newSelectedRepos = [...prev.configuredRepos, { id, base_branch, name }];
      }
      
      // Persist the updated selected repos
      persistSelectedRepos(newSelectedRepos);
      
      return {
        ...prev,
        configuredRepos: newSelectedRepos
      };
    });
  }, [updatePromptsState]);

  const handleGitHubLogin = useCallback(async () => {
    setTimeout(() => {
      updateCurrentRepoStepField('isLoggedIn', true);
    }, 1000);
  }, [updateCurrentRepoStepField]);

  return {
    promptsState,
    filteredPrompts: paginatedPrompts,
    totalPrompts: sortedPrompts.length,
    totalPages,
    currentPrompt: promptsState.currentPrompt,
    createPrompt,
    updatePrompt,
    deletePrompt,
    setCurrentPrompt,
    setSearchQuery,
    setCurrentPage,
    setSortBy,
    setRepoFilter,
    updateCurrentRepoStepField,
    toggleRepoSelection,
    handleGitHubLogin,
  };
}