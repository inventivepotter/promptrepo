import { useCallback, useEffect, useRef } from 'react';
import { ConfigState } from '../_types/state';
import { ConfigService } from '@/services/config/configService';
import type { components } from '@/types/generated/api';

type AppConfigOutput = components['schemas']['AppConfig-Output'];

export const initConfig: AppConfigOutput = {
  hosting_config: { type: "individual" },
  oauth_configs: null,
  llm_configs: null,
  repo_configs: null,
};

export const initConfigState: ConfigState = {
  config: initConfig,
  currentStep: {
    step: 1,
    selectedProvider: "",
    selectedModel: "",
    apiKey: "",
    apiBaseUrl: "",
  },
  providers: {
    available: [],
    configured: [],
    isLoading: false,
  },
  repos: {
    available: [],
    configured: [],
    isLoading: false,
  },
  isLoading: true,
  isSaving: false,
};

export function useInitLoad(
  setConfigState: React.Dispatch<React.SetStateAction<ConfigState>>,
  loadAvailableLLMProviders: () => Promise<void>,
  loadAvailableRepos: () => Promise<void>
) {
  const hasInitialized = useRef(false);

  // Load configuration
  const loadConfig = useCallback(async () => {
    if (hasInitialized.current) return;
    
    setConfigState(prev => ({ ...prev, isLoading: true }));
    
    try {
      const config = await ConfigService.getConfig();
      setConfigState(prev => ({
        ...prev,
        config,
        repos: {
          ...prev.repos,
          configured: config.repo_configs || []
        },
        isLoading: false,
      }));
      hasInitialized.current = true;
    } catch (error) {
      setConfigState(prev => ({
        ...prev,
        config: initConfig,
        isLoading: false,
      }));
    }
  }, [setConfigState]);

  // Initialize on mount
  useEffect(() => {
    loadConfig();
    loadAvailableLLMProviders();
    loadAvailableRepos();
  }, [loadConfig, loadAvailableLLMProviders, loadAvailableRepos]);

  // Set loading states
  const setIsLoading = useCallback((loading: boolean) => {
    setConfigState(prev => ({ ...prev, isLoading: loading }));
  }, [setConfigState]);

  const setIsSaving = useCallback((saving: boolean) => {
    setConfigState(prev => ({ ...prev, isSaving: saving }));
  }, [setConfigState]);

  return {
    loadConfig,
    setIsLoading,
    setIsSaving,
  };
}