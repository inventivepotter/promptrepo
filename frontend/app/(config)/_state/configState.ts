import { useState, useRef, useEffect, useCallback } from "react";
import { ConfigState } from '../_types/state';
import { getConfig } from '../_lib/getConfig';
import { modelsApi } from '../_lib/api/modelsApi';
import { errorNotification } from '@/lib/notifications';
import { safeString, safeArray } from '@/utils/safeValues';
import { getHostingType } from '@/utils/hostingType';
import { getAvailableRepos } from '@/lib/repos/getAvailableRepos';
import { loadConfiguredRepos } from '@/lib/repos/loadConfiguredRepos';
import { Repo } from '@/types/Repo';

export const safeHostingType = (value: string | null | undefined): "individual" | "organization" | "multi-tenant" | "" => {
  const validTypes = ["individual", "organization", "multi-tenant"];
  if (value && validTypes.includes(value)) {
    return value as "individual" | "organization" | "multi-tenant";
  }
  return "individual";
};

export const initConfig: ConfigState['config'] = {
  hostingType: "individual",
  githubClientId: "",
  githubClientSecret: "",
  llmConfigs: [],
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
    isLoading: false,
    error: null,
  },
  repos: {
    available: [],
    configured: [],
    isLoading: false,
    error: null,
  },
  isLoading: true,
  isSaving: false,
  error: {
    isUnauthorized: true,
    hasNoConfig: false,
    message: 'Loading...'
  },
};

export function useConfigState() {
  const [configState, setConfigState] = useState<ConfigState>(initConfigState);
  const hasRestoredSetupData = useRef(false);
  // Global state to prevent duplicate API calls
  const globalLoadingRef = useRef(false);
  const globalDataLoadedRef = useRef(false);
  const providersLoadingRef = useRef(false);
  const providersLoadedRef = useRef(false);
  const reposLoadingRef = useRef(false);
  const reposLoadedRef = useRef(false);

  // Load providers globally
  const loadProviders = useCallback(async () => {
    // Skip if already loaded or currently loading
    if (providersLoadedRef.current || providersLoadingRef.current) {
      return;
    }

    // Get hosting type first to determine if we should skip backend calls
    const hostingType = await getHostingType();
    
    // For organization hosting type, skip providers backend call
    if (hostingType === 'organization') {
      setConfigState(prev => ({
        ...prev,
        providers: {
          available: [],
          isLoading: false,
          error: null,
        }
      }));
      providersLoadedRef.current = true;
      return;
    }

    providersLoadingRef.current = true;
    setConfigState(prev => ({
      ...prev,
      providers: {
        ...prev.providers,
        isLoading: true,
        error: null,
      }
    }));

    try {
      const result = await modelsApi.getAvailableProviders();
      if (result.success && result.data && result.data.providers) {
        setConfigState(prev => ({
          ...prev,
          providers: {
            available: result.data.providers,
            isLoading: false,
            error: null,
          }
        }));
        providersLoadedRef.current = true;
      } else {
        const errorMsg = 'error' in result ? result.error : 'Unknown error';
        setConfigState(prev => ({
          ...prev,
          providers: {
            available: [],
            isLoading: false,
            error: errorMsg,
          }
        }));
      }
    } catch (error) {
      setConfigState(prev => ({
        ...prev,
        providers: {
          available: [],
          isLoading: false,
          error: 'Failed to load providers',
        }
      }));
    } finally {
      providersLoadingRef.current = false;
    }
  }, []);

// Load repos globally with better error handling and race condition prevention
const loadRepos = useCallback(async () => {
  // Skip if already loaded or currently loading
  if (reposLoadedRef.current || reposLoadingRef.current) {
    return;
  }

  reposLoadingRef.current = true;
  setConfigState(prev => ({
    ...prev,
    repos: {
      ...prev.repos,
      isLoading: true,
      error: null,
    }
  }));

  try {
    // Load both available and configured repos concurrently
    const [availableRepos, configuredReposData] = await Promise.all([
      getAvailableRepos(),
      loadConfiguredRepos()
    ]);
    
    // Only update state if we're still the active loading operation
    if (reposLoadingRef.current) {
      setConfigState(prev => ({
        ...prev,
        repos: {
          available: availableRepos,
          configured: configuredReposData,
          isLoading: false,
          error: null,
        }
      }));
      reposLoadedRef.current = true;
    }
  } catch (error) {
    // Only update state if we're still the active loading operation
    if (reposLoadingRef.current) {
      console.error('Failed to load repos:', error);
      setConfigState(prev => ({
        ...prev,
        repos: {
          available: [],
          configured: [],
          isLoading: false,
          error: 'Failed to load repositories',
        }
      }));
    }
  } finally {
    reposLoadingRef.current = false;
  }
}, []);

  useEffect(() => {
    const loadConfig = async () => {
      // Skip if already loaded globally or currently loading
      if (globalDataLoadedRef.current || globalLoadingRef.current) {
        return;
      }

      globalLoadingRef.current = true;
      
      try {
        // Get hosting type first to ensure it's available
        const hostingType = await getHostingType();
        const result = await getConfig();
        
        // Safely handle potential null/undefined values in config
        const safeConfig = {
          hostingType: safeHostingType(result.config?.hostingType || hostingType),
          githubClientId: safeString(result.config?.githubClientId),
          githubClientSecret: safeString(result.config?.githubClientSecret),
          llmConfigs: safeArray(result.config?.llmConfigs),
        };
        
        setConfigState(prev => ({
          ...prev,
          config: safeConfig,
          currentStep: {
            step: 1,
            selectedProvider: "",
            selectedModel: "",
            apiKey: "",
            apiBaseUrl: "",
          },
          isLoading: false,
          error: result.error,
        }));
        
        // Mark as globally loaded only if no error
        if (!result.error) {
          globalDataLoadedRef.current = true;
        }
      } catch (error) {
        globalLoadingRef.current = false;
        setConfigState(prev => ({
          ...prev,
          error: {
            isUnauthorized: false,
            hasNoConfig: false,
            message: 'Failed to load configuration'
          },
          isLoading: false,
        }));
      } finally {
        hasRestoredSetupData.current = true;
        globalLoadingRef.current = false;
      }
    };
    
    loadConfig();
    // Load providers after config
    loadProviders();
    // Load repos after config
    loadRepos();
  }, [loadProviders, loadRepos]);

  const updateConfigState = useCallback((updater: ConfigState | ((prev: ConfigState) => ConfigState)) => {
    setConfigState(prev => {
      const newState = typeof updater === 'function' ? updater(prev) : updater;
      // Don't persist to backend - only persist when user clicks save
      return newState;
    });
  }, []);

  // Generic field updater for config fields
  const updateConfigField = useCallback(<K extends keyof ConfigState['config']>(
    field: K,
    value: ConfigState['config'][K]
  ) => {
    updateConfigState(prev => ({
      ...prev,
      config: { ...prev.config, [field]: value }
    }));
  }, [updateConfigState]);

  const updateCurrentStepField = useCallback((field: keyof ConfigState['currentStep'], value: string | number | boolean) => {
    updateConfigState(prev => ({
      ...prev,
      currentStep: { ...prev.currentStep, [field]: value }
    }));
  }, [updateConfigState]);

  const addLLMConfig = useCallback(() => {
    const currentStep = configState.currentStep;
    if (currentStep.selectedProvider && currentStep.selectedModel && currentStep.apiKey) {
      const newConfig = {
        provider: currentStep.selectedProvider,
        model: currentStep.selectedModel,
        apiKey: currentStep.apiKey,
        apiBaseUrl: currentStep.apiBaseUrl
      };

      // Check for uniqueness: combination of provider, model, apiBaseUrl, and apiKey must be unique
      const isDuplicate = configState.config.llmConfigs.some(existingConfig =>
        existingConfig.provider === newConfig.provider &&
        existingConfig.model === newConfig.model &&
        existingConfig.apiKey === newConfig.apiKey &&
        existingConfig.apiBaseUrl === newConfig.apiBaseUrl
      );

      if (isDuplicate) {
        errorNotification(
          'Duplicate Configuration',
          'This LLM configuration already exists. The combination of provider, model, API base URL, and API key must be unique.'
        );
        return;
      }

      updateConfigState(prev => ({
        ...prev,
        config: {
          ...prev.config,
          llmConfigs: [...prev.config.llmConfigs, newConfig],
        },
        currentStep: {
          ...prev.currentStep,
          selectedProvider: "",
          selectedModel: "",
          apiKey: "",
          apiBaseUrl: ""
        }
      }));
    }
  }, [configState.currentStep, updateConfigState]);

  const removeLLMConfig = useCallback((index: number) => {
    updateConfigState(prev => ({
      ...prev,
      config: {
        ...prev.config,
        llmConfigs: prev.config.llmConfigs.filter((_, i) => i !== index)
      }
    }));
  }, [updateConfigState]);

  const setIsLoading = useCallback((loading: boolean) => {
    updateConfigState(prev => ({
      ...prev,
      isLoading: loading
    }));
  }, [updateConfigState]);

  const setIsSaving = useCallback((saving: boolean) => {
    updateConfigState(prev => ({
      ...prev,
      isSaving: saving
    }));
  }, [updateConfigState]);

  const updateConfiguredRepos = useCallback((repos: Repo[]) => {
    updateConfigState(prev => ({
      ...prev,
      repos: {
        ...prev.repos,
        configured: repos
      }
    }));
  }, [updateConfigState]);

  // Reset loading state function for cleanup
  const resetReposLoading = useCallback(() => {
    reposLoadingRef.current = false;
    reposLoadedRef.current = false;
  }, []);

  return {
    configState,
    setConfigState: updateConfigState,
    updateConfigField,
    updateCurrentStepField,
    addLLMConfig,
    removeLLMConfig,
    setIsLoading,
    setIsSaving,
    loadProviders,
    loadRepos,
    updateConfiguredRepos,
    resetReposLoading,
  };
}