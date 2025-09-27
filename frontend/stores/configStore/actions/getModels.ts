// Get models action for fetching available models from a provider
import type { StateCreator } from '@/lib/zustand';
import { LLMProviderService } from '@/services/llm/llmProvider/llmProviderService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';
import type { components } from '@/types/generated/api';

type ModelInfo = components['schemas']['ModelInfo'];

export const createGetModelsAction: StateCreator<
  ConfigStore,
  [],
  [],
  { 
    getModels: () => Promise<ModelInfo[]>;
    setAvailableModels: (models: ModelInfo[]) => void;
    setLoadingModels: (loading: boolean) => void;
  }
> = (set, get) => {
  return {
    getModels: async () => {
      logStoreAction('ConfigStore', 'getModels');
      
      const { llmProvider, apiKey, apiBaseUrl } = get();
      
      // Check if we have the required fields
      if (!llmProvider || !apiKey || apiKey.length < 3) {
        set((draft) => {
          draft.availableModels = [];
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/getModels/noCredentials');
        return [];
      }

      // Find the current provider to check if it requires custom API base
      const currentProvider = get().availableProviders.find(p => p.id === llmProvider);
      const requiresApiBase = currentProvider?.custom_api_base || false;
      
      // For providers that require API base, check if it's provided
      if (requiresApiBase && (!apiBaseUrl || apiBaseUrl.length < 3)) {
        set((draft) => {
          draft.availableModels = [];
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/getModels/noApiBase');
        return [];
      }

      set((draft) => {
        draft.isLoadingModels = true;
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/getModels/start');

      try {
        const result = await LLMProviderService.getAvailableModels(
          llmProvider,
          apiKey,
          requiresApiBase ? apiBaseUrl : ''
        );

        const models = result.models || [];
        
        set((draft) => {
          draft.availableModels = models;
          draft.isLoadingModels = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/getModels/success');
        
        return models;
      } catch (error) {
        const storeError = handleStoreError(error, 'getModels');
        console.error('Get models error:', error);

        set((draft) => {
          draft.availableModels = [];
          draft.isLoadingModels = false;
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/getModels/error');

        return [];
      }
    },

    setAvailableModels: (models: ModelInfo[]) => {
      set((draft) => {
        draft.availableModels = models;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/setAvailableModels');
    },

    setLoadingModels: (loading: boolean) => {
      set((draft) => {
        draft.isLoadingModels = loading;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/setLoadingModels');
    },
  };
};