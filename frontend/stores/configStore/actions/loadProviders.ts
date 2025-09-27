// Load providers action
import type { StateCreator } from '@/lib/zustand';
import { LLMProviderService } from '@/services/llm/llmProvider/llmProviderService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createLoadProvidersAction: StateCreator<
  ConfigStore,
  [],
  [],
  { loadProviders: () => Promise<void> }
> = (set, get) => {
  return {
    loadProviders: async () => {
      logStoreAction('ConfigStore', 'loadProviders');
      
      set((draft) => {
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/loadProviders/start');

      try {
        // Check if we already have providers data (from localStorage hydration)
        const currentState = get();
        if (currentState.availableProviders && currentState.availableProviders.length > 0) {
          // We have valid providers data, no need to call API
          logStoreAction('ConfigStore', 'loadProviders/skip - data from localStorage');
          return;
        }

        const providersResponse = await LLMProviderService.getAvailableProviders();
        
        set((draft) => {
          draft.availableProviders = providersResponse.providers || [];
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/loadProviders/success');
      } catch (error) {
        const storeError = handleStoreError(error, 'loadProviders');
        console.error('Load providers error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/loadProviders/error');
      }
    },
  };
};