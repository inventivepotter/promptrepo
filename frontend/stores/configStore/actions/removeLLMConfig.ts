// Remove LLM config action
import type { StateCreator } from '@/lib/zustand';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createRemoveLLMConfigAction: StateCreator<
  ConfigStore,
  [],
  [],
  { removeLLMConfig: (index: number) => void }
> = (set) => {
  return {
    removeLLMConfig: (index: number) => {
      logStoreAction('ConfigStore', 'removeLLMConfig', { index });
      
      try {
        set((draft) => {
          if (draft.config.llm_configs && index >= 0 && index < draft.config.llm_configs.length) {
            draft.config.llm_configs.splice(index, 1);
          }
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/removeLLMConfig');
      } catch (error) {
        const storeError = handleStoreError(error, 'removeLLMConfig');
        console.error('Remove LLM config error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/removeLLMConfig/error');
        
        throw error;
      }
    },
  };
};