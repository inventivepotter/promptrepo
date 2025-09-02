import { PromptsState } from '../_types/PromptState';
import { Prompt } from '@/types/Prompt';
import { useState, useRef, useEffect, useCallback } from 'react';
import { loadConfiguredRepos } from '../../../lib/repos/loadConfiguredRepos';
import { loadConfiguredModels } from './loadConfiguredModels';
import { loadPrompts, persistPromptsToBrowserStorage } from './loadPrompts';
import { useManagePrompts } from './managePrompt';
import { useManagePromptsList } from './managePromptsList';
import { useAuth } from '../../(auth)/_components/AuthProvider';

export function usePromptsState() {
  const [promptsState, setPromptsState] = useState<PromptsState>(defaultPromptsState);
  const hasRestoredData = useRef(false);
  const { user } = useAuth();

  useEffect(() => {
    if (!hasRestoredData.current && typeof window !== "undefined") {
      // Initialize data loading
      const initializeData = async () => {
        try {
          // Load configured repos and models from localStorage with API fallback
          const configuredRepos = await loadConfiguredRepos();
          const configuredModels = await loadConfiguredModels();
          const prompts = await loadPrompts();

          setPromptsState(prev => ({
            ...prev,
            prompts: prompts,
            configuredRepos: configuredRepos,
            configuredModels: configuredModels,
          }));
        } catch (error) {
          throw error;
        }
      };

      initializeData();
      hasRestoredData.current = true;
    }
  }, [user?.id]);

  const updatePromptsState = useCallback((updater: PromptsState | ((prev: PromptsState) => PromptsState), shouldPersist: boolean = false) => {
    setPromptsState(prev => {
      const newState = typeof updater === 'function' ? updater(prev) : updater;
      // Only persist prompts when explicitly requested (e.g., on save)
      if (shouldPersist) {
        persistPromptsToBrowserStorage(newState.prompts);
      }
      return newState;
    });
  }, []);

  const promptManagement = useManagePrompts(updatePromptsState, defaultPrompt);
  const promptsListManagement = useManagePromptsList(promptsState, updatePromptsState);

  return {
    promptsState,
    filteredPrompts: promptsListManagement.computed.paginatedPrompts,
    totalPrompts: promptsListManagement.computed.totalPrompts,
    totalPages: promptsListManagement.computed.totalPages,
    currentPrompt: promptsState.currentPrompt,
    ...promptManagement,
    ...promptsListManagement.functions,
  };
}

export const defaultPrompt: Omit<Prompt, 'id' | 'created_at' | 'updated_at'> = {
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

export const defaultPromptsState: PromptsState = {
  prompts: [],
  currentPrompt: null,
  searchQuery: "",
  currentPage: 1,
  itemsPerPage: 9,
  sortBy: 'updated_at',
  sortOrder: 'desc',
  configuredRepos: [],
  configuredModels: [],
  repoFilter: "",
};
