// Update config action
import type { StateCreator } from '@/lib/zustand';
import { ConfigService } from '@/services/config/configService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import { successNotification } from '@/lib/notifications';
import type { ConfigStore, AppConfigInput } from '../types';

export const createUpdateConfigAction: StateCreator<
  ConfigStore,
  [],
  [],
  { updateConfig: (config: AppConfigInput) => Promise<void> }
> = (set) => {
  return {
    updateConfig: async (config: AppConfigInput) => {
      logStoreAction('ConfigStore', 'updateConfig', config);
      
      set((draft) => {
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/updateConfig/start');

      try {
        await ConfigService.updateConfig(config);
        
        set((draft) => {
          draft.config = { ...draft.config, ...config };
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/updateConfig/success');
        
        successNotification('Configuration Updated', 'Your configuration has been successfully updated.');
      } catch (error) {
        const storeError = handleStoreError(error, 'updateConfig');
        console.error('Update config error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/updateConfig/error');
        
        throw error;
      }
    },
  };
};