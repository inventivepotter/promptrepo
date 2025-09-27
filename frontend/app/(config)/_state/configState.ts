import { useState, useCallback } from "react";
import { ConfigState } from '../_types/state';
import { useLLMConfigActions } from './manageLLMConfigs';
import { useRepoConfigActions } from './manageRepoConfigs';
import { useInitLoad, initConfigState } from './initLoad';
import type { components } from '@/types/generated/api';

type AppConfigOutput = components['schemas']['AppConfig-Output'];

export function useConfigState() {
  const [configState, setConfigState] = useState<ConfigState>(initConfigState);

  // Import LLM config actions
  const llmActions = useLLMConfigActions(configState, setConfigState);
  
  // Import repo config actions
  const repoActions = useRepoConfigActions(configState, setConfigState);
  
  // Import initialization logic
  const initActions = useInitLoad(
    setConfigState, 
    llmActions.loadAvailableLLMProviders, 
    repoActions.loadAvailableRepos
  );

  // Update config field
  const updateConfigField = useCallback(<K extends keyof AppConfigOutput>(
    field: K,
    value: AppConfigOutput[K]
  ) => {
    setConfigState(prev => ({
      ...prev,
      config: { ...prev.config, [field]: value }
    }));
  }, []);

  // Update current step field
  const updateCurrentStepField = useCallback((
    field: keyof ConfigState['currentStep'], 
    value: string | number
  ) => {
    setConfigState(prev => ({
      ...prev,
      currentStep: { ...prev.currentStep, [field]: value }
    }));
  }, []);

  return {
    configState,
    setConfigState: setConfigState,
    updateConfigField,
    updateCurrentStepField,
    
    // LLM config actions
    addLLMConfig: llmActions.addLLMConfig,
    removeLLMConfig: llmActions.removeLLMConfig,
    loadAvailableLLMProviders: llmActions.loadAvailableLLMProviders,
    
    // Repo config actions
    addRepoConfig: repoActions.addRepoConfig,
    removeRepoConfig: repoActions.removeRepoConfig,
    loadAvailableRepos: repoActions.loadAvailableRepos,
    updateConfiguredRepos: repoActions.updateConfiguredRepos,
    
    // Init and loading actions
    setIsLoading: initActions.setIsLoading,
    setIsSaving: initActions.setIsSaving,
    
    // Legacy placeholder
    resetReposLoading: () => {},
  };
}