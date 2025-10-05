// Hooks for selective subscriptions to config store
import { useConfigStore } from './configStore';

// Hook for config data
export const useConfig = () => useConfigStore((state) => state.config);

// Hook for hosting type
export const useHostingType = () => useConfigStore((state) => state.config.hosting_config?.type ?? null);

// Hook for available providers
export const useAvailableProviders = () => useConfigStore((state) => state.availableLLMProviders);

// Hook for available repos
export const useAvailableRepos = () => useConfigStore((state) => state.availableRepos);

// Hook for available branches
export const useAvailableBranches = () => useConfigStore((state) => state.availableBranches);

// Hook for loading branches state
export const useIsLoadingBranches = () => useConfigStore((state) => state.isLoadingBranches);

// Hook for loading config state
export const useIsLoadingConfig = () => useConfigStore((state) => state.isLoadingConfig);

// Hook for error state
export const useConfigError = () => useConfigStore((state) => state.error);

// Hooks for repo form state
export const useSelectedRepo = () => useConfigStore((state) => state.selectedRepo);
export const useSelectedBranch = () => useConfigStore((state) => state.selectedBranch);
export const useIsSavingRepo = () => useConfigStore((state) => state.isSaving);
export const useRepoSearchValue = () => useConfigStore((state) => state.repoSearchValue);
export const useBranchSearchValue = () => useConfigStore((state) => state.branchSearchValue);

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

// Hook for LLM form UI state
export const useLLMFormUIState = () => {
  const providerSearchValue = useConfigStore((state) => state.providerSearchValue);
  const modelSearchValue = useConfigStore((state) => state.modelSearchValue);
  
  return {
    providerSearchValue,
    modelSearchValue,
  };
};

// Hook for repo form state
export const useRepoFormState = () => {
  const selectedRepo = useConfigStore((state) => state.selectedRepo);
  const selectedBranch = useConfigStore((state) => state.selectedBranch);
  const isSaving = useConfigStore((state) => state.isSaving);
  const repoSearchValue = useConfigStore((state) => state.repoSearchValue);
  const branchSearchValue = useConfigStore((state) => state.branchSearchValue);
  
  return {
    selectedRepo,
    selectedBranch,
    isSaving,
    repoSearchValue,
    branchSearchValue,
  };
};

// Hook for config actions
export const useConfigActions = () => {
  const {
    getConfig,
    updateConfig,
    initializeConfig,
    addLLMConfig,
    removeLLMConfig,
    loadAvailableLLMProviders,
    getModels,
    setLLMProvider,
    setLLMProviderWithSideEffects,
    fetchModelsIfReady,
    setApiKey,
    setLLMModel,
    setApiBaseUrl,
    resetLLMForm,
    setAvailableModels,
    setLoadingModels,
    setLoadingConfig,
    addRepoConfig,
    removeRepoConfig,
    loadAvailableRepos,
    updateConfiguredRepos,
    fetchBranches,
    resetBranches,
    setSelectedRepo,
    setSelectedRepoWithSideEffects,
    setSelectedBranch,
    setIsSaving,
    setRepoSearchValue,
    setBranchSearchValue,
    resetRepoForm,
    setProviderSearchValue,
    setModelSearchValue,
  } = useConfigStore();

  return {
    getConfig,
    updateConfig,
    initializeConfig,
    addLLMConfig,
    removeLLMConfig,
    loadAvailableLLMProviders,
    getModels,
    setLLMProvider,
    setLLMProviderWithSideEffects,
    fetchModelsIfReady,
    setApiKey,
    setLLMModel,
    setApiBaseUrl,
    resetLLMForm,
    setAvailableModels,
    setLoadingModels,
    setLoadingConfig,
    addRepoConfig,
    removeRepoConfig,
    loadAvailableRepos,
    updateConfiguredRepos,
    fetchBranches,
    resetBranches,
    setSelectedRepo,
    setSelectedRepoWithSideEffects,
    setSelectedBranch,
    setIsSaving,
    setRepoSearchValue,
    setBranchSearchValue,
    resetRepoForm,
    setProviderSearchValue,
    setModelSearchValue,
  };
};

// Hook for complete config state
export const useConfigState = () => {
  const config = useConfig();
  const availableProviders = useAvailableProviders();
  const availableRepos = useAvailableRepos();
  const error = useConfigError();

  return {
    config,
    availableProviders,
    availableRepos,
    error,
  };
};