// Add LLM config action
import type { StateCreator } from '@/lib/zustand';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore, LLMConfig } from '../types';

export const createAddLLMConfigAction: StateCreator<
  ConfigStore,
  [],
  [],
  { addLLMConfig: (config: LLMConfig) => void }
> = (set) => {
  return {
    addLLMConfig: (config: LLMConfig) => {
      logStoreAction('ConfigStore', 'addLLMConfig', config);
      
      try {
        set((draft) => {
          const currentConfigs = draft.config.llm_configs || [];
          draft.config.llm_configs = [...currentConfigs, config];
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/addLLMConfig');
      } catch (error) {
        const storeError = handleStoreError(error, 'addLLMConfig');
        console.error('Add LLM config error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/addLLMConfig/error');
        
        throw error;
      }
    },
  };
};