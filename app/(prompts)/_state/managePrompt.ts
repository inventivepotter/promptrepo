import { useCallback } from 'react';
import { Prompt } from '@/types/Prompt';
import { PromptsState } from '../_types/PromptState';

export type PromptStateUpdater = (
  updater: PromptsState | ((prev: PromptsState) => PromptsState),
  shouldPersist?: boolean
) => void;

export interface PromptManagementFunctions {
  createPrompt: () => Prompt;
  updatePrompt: (id: string, updates: Partial<Omit<Prompt, 'id' | 'created_at' | 'updated_at'>>) => void;
  deletePrompt: (id: string) => void;
  setCurrentPrompt: (prompt: Prompt | null) => void;
}

export function useManagePrompts(
  updatePromptsState: PromptStateUpdater,
  defaultPrompt: Omit<Prompt, 'id' | 'created_at' | 'updated_at'>
): PromptManagementFunctions {
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
    }), true);

    return newPrompt;
  }, [updatePromptsState, defaultPrompt]);

  const updatePrompt = useCallback((id: string, updates: Partial<Omit<Prompt, 'id' | 'created_at' | 'updated_at'>>) => {
    updatePromptsState(prev => ({
      ...prev,
      prompts: prev.prompts.map((prompt) => prompt.id === id
        ? { ...prompt, ...updates, updated_at: new Date() }
        : prompt
      ),
      currentPrompt: prev.currentPrompt?.id === id
        ? { ...prev.currentPrompt, ...updates, updated_at: new Date() }
        : prev.currentPrompt,
    }), true);
  }, [updatePromptsState]);

  const deletePrompt = useCallback((id: string) => {
    updatePromptsState(prev => ({
      ...prev,
      prompts: prev.prompts.filter((prompt) => prompt.id !== id),
      currentPrompt: prev.currentPrompt?.id === id ? null : prev.currentPrompt,
    }), true); // Persist when deleting prompt
  }, [updatePromptsState]);

  const setCurrentPrompt = useCallback((prompt: Prompt | null) => {
    updatePromptsState(prev => ({ ...prev, currentPrompt: prompt }));
  }, [updatePromptsState]);

  return {
    createPrompt,
    updatePrompt,
    deletePrompt,
    setCurrentPrompt,
  };
}