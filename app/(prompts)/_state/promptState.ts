import { useState, useRef, useEffect, useCallback } from "react";
import { getPromptsFromPersistance } from '../_lib/getPromptsFromPersistance';
import { SelectedRepo } from "../_components/Repos";

export interface Prompt {
  id: string;
  name: string;
  description: string;
  prompt: string;
  model: string;
  failover_model: string;
  temperature: number;
  top_p: number;
  max_tokens: number;
  thinking_enabled: boolean;
  thinking_budget: number;
  repo?: SelectedRepo;
  created_at: Date;
  updated_at: Date;
}

export interface PromptsState {
  prompts: Prompt[];
  currentPrompt: Prompt | null;
  searchQuery: string;
  currentPage: number;
  itemsPerPage: number;
  sortBy: 'name' | 'updated_at';
  sortOrder: 'asc' | 'desc';
  selectedRepos: Array<SelectedRepo>;
  repoFilter: string;
  currentRepoStep: {
    isLoggedIn: boolean;
    selectedRepo: string;
    selectedBranch: string;
  };
}

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
  selectedRepos: [],
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
    window.localStorage.setItem("promptsData", JSON.stringify(prompts));
  }
};

// Persistence helper for selected repos
const persistSelectedRepos = (selectedRepos: PromptsState['selectedRepos']) => {
  if (typeof window !== "undefined") {
    window.localStorage.setItem("selectedRepos", JSON.stringify(selectedRepos));
  }
};

// Load selected repos from localStorage
const loadSelectedRepos = (): PromptsState['selectedRepos'] => {
  if (typeof window !== "undefined") {
    const saved = window.localStorage.getItem("selectedRepos");
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (error) {
        console.error("Failed to restore selected repos:", error);
      }
    }
  }
  return [];
};

export function usePromptsState() {
  const [promptsState, setPromptsState] = useState<PromptsState>(defaultPromptsState);
  const hasRestoredData = useRef(false);

  useEffect(() => {
    if (!hasRestoredData.current && typeof window !== "undefined") {
      // Load prompts from localStorage
      const saved = window.localStorage.getItem("promptsData");
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
              selectedRepos: loadSelectedRepos() // Load saved repos
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
          selectedRepos: loadSelectedRepos() // Load saved repos
        }));
        persistPrompts(mockPrompts);
      }
      hasRestoredData.current = true;
    }
  }, []);

  const updatePromptsState = useCallback((updater: PromptsState | ((prev: PromptsState) => PromptsState)) => {
    setPromptsState(prev => {
      const newState = typeof updater === 'function' ? updater(prev) : updater;
      // Persist prompts whenever state changes
      persistPrompts(newState.prompts);
      return newState;
    });
  }, []);

  const createPrompt = useCallback((selectedRepo?: { id: number; branch: string; name: string }) => {
    const newPrompt: Prompt = {
      ...defaultPrompt,
      id: `prompt_${Date.now()}_${Math.random().toString(36).substring(2)}`,
      created_at: new Date(),
      updated_at: new Date(),
      repo: selectedRepo,
    };
    
    updatePromptsState(prev => ({
      ...prev,
      prompts: [newPrompt, ...prev.prompts],
      currentPrompt: newPrompt,
    }));
    
    return newPrompt;
  }, [updatePromptsState]);

  const updatePrompt = useCallback((id: string, updates: Partial<Omit<Prompt, 'id' | 'created_at' | 'updated_at'>>) => {
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
    }));
  }, [updatePromptsState]);

  const deletePrompt = useCallback((id: string) => {
    updatePromptsState(prev => ({
      ...prev,
      prompts: prev.prompts.filter(prompt => prompt.id !== id),
      currentPrompt: prev.currentPrompt?.id === id ? null : prev.currentPrompt,
    }));
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

  const toggleRepoSelection = useCallback((id: number, branch: string, name: string) => {
    updatePromptsState(prev => {
      const existingIndex = prev.selectedRepos.findIndex(r => r.id === id);
      let newSelectedRepos;
      
      if (existingIndex >= 0) {
        const existing = prev.selectedRepos[existingIndex];
        if (existing.branch === branch) {
          newSelectedRepos = prev.selectedRepos.filter(r => r.id !== id);
        } else {
          newSelectedRepos = prev.selectedRepos.map((r, i) =>
            i === existingIndex ? { ...r, branch } : r
          );
        }
      } else {
        newSelectedRepos = [...prev.selectedRepos, { id, branch, name }];
      }
      
      // Persist the updated selected repos
      persistSelectedRepos(newSelectedRepos);
      
      return {
        ...prev,
        selectedRepos: newSelectedRepos
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