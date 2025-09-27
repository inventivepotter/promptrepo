// LLM-specific actions for config store
import type { StateCreator } from '@/lib/zustand';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createLLMActions: StateCreator<
  ConfigStore,
  [],
  [],
  {
    setLLMProvider: (provider: string) => void;
    setApiKey: (apiKey: string) => void;
    setLLMModel: (model: string) => void;
    setApiBaseUrl: (url: string) => void;
    resetLLMForm: () => void;
  }
> = (set) => {
  return {
    setLLMProvider: (provider: string) => {
      logStoreAction('ConfigStore', 'setLLMProvider', { provider });
      
      try {
        set((draft) => {
          draft.llmProvider = provider;
          // Reset model when provider changes
          draft.llmModel = '';
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setLLMProvider');
      } catch (error) {
        const storeError = handleStoreError(error, 'setLLMProvider');
        console.error('Set LLM provider error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setLLMProvider/error');
      }
    },

    setApiKey: (apiKey: string) => {
      logStoreAction('ConfigStore', 'setApiKey');
      
      try {
        set((draft) => {
          draft.apiKey = apiKey;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setApiKey');
      } catch (error) {
        const storeError = handleStoreError(error, 'setApiKey');
        console.error('Set API key error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setApiKey/error');
      }
    },

    setLLMModel: (model: string) => {
      logStoreAction('ConfigStore', 'setLLMModel', { model });
      
      try {
        set((draft) => {
          draft.llmModel = model;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setLLMModel');
      } catch (error) {
        const storeError = handleStoreError(error, 'setLLMModel');
        console.error('Set LLM model error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setLLMModel/error');
      }
    },

    setApiBaseUrl: (url: string) => {
      logStoreAction('ConfigStore', 'setApiBaseUrl', { url });
      
      try {
        set((draft) => {
          draft.apiBaseUrl = url;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setApiBaseUrl');
      } catch (error) {
        const storeError = handleStoreError(error, 'setApiBaseUrl');
        console.error('Set API base URL error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setApiBaseUrl/error');
      }
    },

    resetLLMForm: () => {
      logStoreAction('ConfigStore', 'resetLLMForm');
      
      try {
        set((draft) => {
          draft.llmProvider = '';
          draft.apiKey = '';
          draft.llmModel = '';
          draft.apiBaseUrl = '';
          draft.availableModels = [];
          draft.isLoadingModels = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/resetLLMForm');
      } catch (error) {
        const storeError = handleStoreError(error, 'resetLLMForm');
        console.error('Reset LLM form error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/resetLLMForm/error');
      }
    },
  };
};