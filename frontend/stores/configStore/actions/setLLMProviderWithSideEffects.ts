import type { StateCreator } from '@/lib/zustand';
import type { ConfigStore, ConfigActions } from '../types';

export const createSetLLMProviderWithSideEffectsAction: StateCreator<
  ConfigStore,
  [['zustand/immer', never]],
  [],
  Pick<ConfigActions, 'setLLMProviderWithSideEffects'>
> = (set, get) => ({
  setLLMProviderWithSideEffects: async (provider: string) => {
    // First set the selected provider
    set((draft) => {
      draft.llmProvider = provider;
    });

    // If a provider is selected, and other conditions are met, fetch its models
    if (provider) {
      const state = get();
      const { apiKey, apiBaseUrl, availableLLMProviders } = state;
      const { getModels, setLoadingModels } = state;

      // Find the current provider to check if it requires custom API base
      const currentProvider = availableLLMProviders.find((p) => p.id === provider);
      const requiresApiBase = currentProvider?.custom_api_base || false;

      if (!apiKey || apiKey.length < 3) {
        return;
      }

      // For providers that require API base, wait until it's provided
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
    } else {
      // If no provider is selected, reset available models
      set((draft) => {
        draft.availableModels = [];
      });
    }
  },
});