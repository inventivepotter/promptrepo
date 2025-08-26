import { useState, useRef, useEffect, useCallback } from "react";
import { getPromptsFromPersistance } from '../_lib/getPromptsFromPersistance';

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
};

// Persistence helper
const persistPrompts = (prompts: Prompt[]) => {
  if (typeof window !== "undefined") {
    window.localStorage.setItem("promptsData", JSON.stringify(prompts));
  }
};

export function usePromptsState() {
  const [promptsState, setPromptsState] = useState<PromptsState>(defaultPromptsState);
  const hasRestoredData = useRef(false);

  useEffect(() => {
    if (!hasRestoredData.current && typeof window !== "undefined") {
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
            setPromptsState(prev => ({ ...prev, prompts: mergedPrompts }));
            persistPrompts(mergedPrompts);
          }
        } catch (error) {
          console.error("Failed to restore prompts data:", error);
        }
      } else {
        // If nothing in localStorage, insert all from getPrompts
        const mockPrompts = getPromptsFromPersistance();
        setPromptsState(prev => ({ ...prev, prompts: mockPrompts }));
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
  const filteredPrompts = promptsState.prompts.filter(prompt =>
    prompt.name.toLowerCase().includes(promptsState.searchQuery.toLowerCase()) ||
    prompt.description.toLowerCase().includes(promptsState.searchQuery.toLowerCase())
  );

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
  };
}