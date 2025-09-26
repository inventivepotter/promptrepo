// Hooks for selective subscriptions to config store
import { useConfigStore } from './configStore';

// Hook for config data
export const useConfig = () => useConfigStore((state) => state.config);

// Hook for hosting type
export const useHostingType = () => useConfigStore((state) => state.hostingType);

// Hook for available providers
export const useAvailableProviders = () => useConfigStore((state) => state.availableProviders);

// Hook for available repos
export const useAvailableRepos = () => useConfigStore((state) => state.availableRepos);

// Hook for error state
export const useConfigError = () => useConfigStore((state) => state.error);

// Hook for config actions
export const useConfigActions = () => {
  const {
    getConfig,
    updateConfig,
    getHostingType,
    addLLMConfig,
    removeLLMConfig,
    loadProviders,
    addRepoConfig,
    removeRepoConfig,
    loadRepos,
    updateConfiguredRepos,
  } = useConfigStore();
  
  return {
    getConfig,
    updateConfig,
    getHostingType,
    addLLMConfig,
    removeLLMConfig,
    loadProviders,
    addRepoConfig,
    removeRepoConfig,
    loadRepos,
    updateConfiguredRepos,
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