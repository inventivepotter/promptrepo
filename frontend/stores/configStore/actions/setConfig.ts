// Set config action
import type { StateCreator } from '@/lib/zustand';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore, AppConfigOutput } from '../types';

export const createSetConfigAction: StateCreator<
  ConfigStore,
  [],
  [],
  { setConfig: (config: AppConfigOutput) => void }
> = (set) => {
  return {
    setConfig: (config: AppConfigOutput) => {
      logStoreAction('ConfigStore', 'setConfig', { config });
      
      try {
        set((draft) => {
          draft.config = config;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setConfig');
      } catch (error) {
        const storeError = handleStoreError(error, 'setConfig');
        console.error('Set config error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setConfig/error');
        
        throw error;
      }
    },
  };
};