import { useCallback } from 'react';
import { PromptsState } from '../_types/PromptState';
import { persistConfiguredReposToBrowserStorage } from './loadConfiguredRepos';

export type PromptStateUpdater = (
  updater: PromptsState | ((prev: PromptsState) => PromptsState),
  shouldPersist?: boolean
) => void;

export interface RepoConfigurationFunctions {
  updateCurrentRepoStepField: (field: keyof PromptsState['currentRepoStep'], value: string | boolean) => void;
  toggleRepoSelection: (id: string, base_branch: string, name: string) => void;
}

export function useManageRepoConfiguration(
  updatePromptsState: PromptStateUpdater
): RepoConfigurationFunctions {
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
          newSelectedRepos = prev.configuredRepos.map((r, i) => i === existingIndex ? { ...r, base_branch: base_branch } : r
          );
        }
      } else {
        newSelectedRepos = [...prev.configuredRepos, { id, base_branch, name }];
      }

      // Persist the updated selected repos
      persistConfiguredReposToBrowserStorage(newSelectedRepos);

      return {
        ...prev,
        configuredRepos: newSelectedRepos
      };
    });
  }, [updatePromptsState]);

  return {
    updateCurrentRepoStepField,
    toggleRepoSelection,
  };
}