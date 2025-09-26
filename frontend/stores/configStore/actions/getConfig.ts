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
> = (set) => {
  return {
    getConfig: async () => {
      logStoreAction('ConfigStore', 'getConfig');
      
      set((draft) => {
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/getConfig/start');

      try {
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