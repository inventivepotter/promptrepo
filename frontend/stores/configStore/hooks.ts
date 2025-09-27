// Hooks for selective subscriptions to config store
import { useConfigStore } from './configStore';

// Hook for config data
export const useConfig = () => useConfigStore((state) => state.config);

// Hook for hosting type
export const useHostingType = () => useConfigStore((state) => state.hostingType);

// Hook for available providers
export const useAvailableProviders = () => useConfigStore((state) => state.availableLLMProviders);

// Hook for available repos
export const useAvailableRepos = () => useConfigStore((state) => state.availableRepos);

// Hook for available branches
export const useAvailableBranches = () => useConfigStore((state) => state.availableBranches);

// Hook for loading branches state
export const useIsLoadingBranches = () => useConfigStore((state) => state.isLoadingBranches);

// Hook for error state
export const useConfigError = () => useConfigStore((state) => state.error);

// Hook for LLM form state
export const useLLMFormState = () => {
  const llmProvider = useConfigStore((state) => state.llmProvider);
  const apiKey = useConfigStore((state) => state.apiKey);
  const llmModel = useConfigStore((state) => state.llmModel);
  const apiBaseUrl = useConfigStore((state) => state.apiBaseUrl);
  const availableModels = useConfigStore((state) => state.availableModels);
  const isLoadingModels = useConfigStore((state) => state.isLoadingModels);
  
  return {
    llmProvider,
    apiKey,
    llmModel,
    apiBaseUrl,
    availableModels,
    isLoadingModels,
  };
};

// Hook for config actions
export const useConfigActions = () => {
  const {
    getConfig,
    updateConfig,
    getHostingType,
    addLLMConfig,
    removeLLMConfig,
    loadAvailableLLMProviders,
    getModels,
    setLLMProvider,
    setApiKey,
    setLLMModel,
    setApiBaseUrl,
    resetLLMForm,
    setAvailableModels,
    setLoadingModels,
    addRepoConfig,
    removeRepoConfig,
    loadAvailableRepos,
    updateConfiguredRepos,
    fetchBranches,
    resetBranches,
  } = useConfigStore();

  return {
    getConfig,
    updateConfig,
    getHostingType,
    addLLMConfig,
    removeLLMConfig,
    loadAvailableLLMProviders,
    getModels,
    setLLMProvider,
    setApiKey,
    setLLMModel,
    setApiBaseUrl,
    resetLLMForm,
    setAvailableModels,
    setLoadingModels,
    addRepoConfig,
    removeRepoConfig,
    loadAvailableRepos,
    updateConfiguredRepos,
    fetchBranches,
    resetBranches,
  };
};

// Hook for complete config state
export const useConfigState = () => {
  const config = useConfig();
  const hostingType = useHostingType();
  const availableProviders = useAvailableProviders();
  const availableRepos = useAvailableRepos();
  const error = useConfigError();

  return {
    config,
    hostingType,
    availableProviders,
    availableRepos,
    error,
  };
};