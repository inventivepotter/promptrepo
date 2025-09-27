// Load providers action
import type { StateCreator } from '@/lib/zustand';
import { LLMProviderService } from '@/services/llm/llmProvider/llmProviderService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createLoadProvidersAction: StateCreator<
  ConfigStore,
  [],
  [],
  { loadAvailableLLMProviders: () => Promise<void> }
> = (set, get) => {
  return {
    loadAvailableLLMProviders: async () => {
      logStoreAction('ConfigStore', 'loadAvailableLLMProviders');
      
      set((draft) => {
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/loadAvailableLLMProviders/start');

      try {
        // Check if we already have providers data (from localStorage hydration)
        const currentState = get();
        if (currentState.availableLLMProviders && currentState.availableLLMProviders.length > 0) {
          // We have valid providers data, no need to call API
          logStoreAction('ConfigStore', 'loadAvailableLLMProviders/skip - data from localStorage');
          return;
        }

        const providersResponse = await LLMProviderService.getAvailableProviders();
        
        set((draft) => {
          draft.availableLLMProviders = providersResponse.providers || [];
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/loadAvailableLLMProviders/success');
      } catch (error) {
        const storeError = handleStoreError(error, 'loadAvailableLLMProviders');
        console.error('Load providers error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/loadAvailableLLMProviders/error');
      }
    },
  };
};