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
> = (set) => {
  return {
    loadProviders: async () => {
      logStoreAction('ConfigStore', 'loadProviders');
      
      set((draft) => {
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/loadProviders/start');

      try {
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