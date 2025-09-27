// Get config action
import type { StateCreator } from '@/lib/zustand';
import { ConfigService } from '@/services/config/configService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createGetConfigAction: StateCreator<
  ConfigStore,
  [],
  [],
  { getConfig: () => Promise<void> }
> = (set, get) => {
  return {
    getConfig: async () => {
      logStoreAction('ConfigStore', 'getConfig');
      
      set((draft) => {
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/getConfig/start');

      try {
        // Check if we already have config data (from localStorage hydration)
        const currentState = get();
        if (currentState.config &&
            currentState.config.hosting_config &&
            currentState.config.llm_configs !== undefined &&
            currentState.config.repo_configs !== undefined) {
          // We have valid config data, no need to call API
          logStoreAction('ConfigStore', 'getConfig/skip - data from localStorage');
          return;
        }

        const config = await ConfigService.getConfig();
        
        set((draft) => {
          draft.config = config;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/getConfig/success');
      } catch (error) {
        const storeError = handleStoreError(error, 'getConfig');
        console.error('Get config error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/getConfig/error');
        
        throw error;
      }
    },
  };
};