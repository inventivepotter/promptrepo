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
        const hasValidProviders = currentState.availableLLMProviders &&
          currentState.availableLLMProviders.length > 0 &&
          // Check if the providers have actual data, not just empty objects
          currentState.availableLLMProviders.some(provider => provider.name && provider.name !== '');
          
        if (hasValidProviders) {
          // We have valid providers data, no need to call API
          logStoreAction('ConfigStore', 'loadAvailableLLMProviders/skip - data from localStorage');
          return;
        }

        // If we get here, we don't have valid providers data in localStorage, so fetch from API
        logStoreAction('ConfigStore', 'loadAvailableLLMProviders/fetching from API - no data in localStorage');
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