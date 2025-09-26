// Get hosting type action
import type { StateCreator } from '@/lib/zustand';
import { ConfigService } from '@/services/config/configService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createGetHostingTypeAction: StateCreator<
  ConfigStore,
  [],
  [],
  { getHostingType: () => Promise<void> }
> = (set) => {
  return {
    getHostingType: async () => {
      logStoreAction('ConfigStore', 'getHostingType');
      
      set((draft) => {
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/getHostingType/start');

      try {
        const hostingType = await ConfigService.getHostingType();
        
        set((draft) => {
          draft.hostingType = hostingType;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/getHostingType/success');
      } catch (error) {
        const storeError = handleStoreError(error, 'getHostingType');
        console.error('Get hosting type error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/getHostingType/error');

      }
    },
  };
};