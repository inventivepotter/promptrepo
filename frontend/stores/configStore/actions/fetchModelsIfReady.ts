import type { StateCreator } from '@/lib/zustand';
import type { ConfigStore, ConfigActions } from '../types';

export const createFetchModelsIfReadyAction: StateCreator<
  ConfigStore,
  [['zustand/immer', never]],
  [],
  Pick<ConfigActions, 'fetchModelsIfReady'>
> = (set, get) => ({
  fetchModelsIfReady: async () => {
    const state = get();
    const {
      llmProvider,
      apiKey,
      apiBaseUrl,
      availableLLMProviders,
      getModels,
      setLoadingModels,
    } = state;

    if (!llmProvider) {
      return;
    }

    const currentProvider = availableLLMProviders.find((p) => p.id === llmProvider);
    const requiresApiBase = currentProvider?.custom_api_base || false;

    if (!apiKey || apiKey.length < 3) {
      return;
    }

    if (requiresApiBase && (!apiBaseUrl || apiBaseUrl.length < 3)) {
      return;
    }

    const isMounted = { current: true };
    const fetchData = async () => {
      setLoadingModels(true);
      try {
        await getModels();
      } catch (error) {
        console.error('Error fetching models:', error);
      } finally {
        if (isMounted.current) {
          setLoadingModels(false);
        }
      }
    };

    fetchData();
  },
});