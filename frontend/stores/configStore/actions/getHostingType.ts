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
> = (set, get) => {
  return {
    getHostingType: async () => {
      logStoreAction('ConfigStore', 'getHostingType');
      
      set((draft) => {
        draft.error = null;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/getHostingType/start');

      try {
        // Check if we already have hostingType data (from localStorage hydration)
        const currentState = get();
        const hasValidHostingType = currentState.hostingType !== null &&
          currentState.hostingType !== undefined &&
          currentState.hostingType !== ''; // Check if it's not an empty string
          
        if (hasValidHostingType) {
          // We have valid hostingType data, no need to call API
          logStoreAction('ConfigStore', 'getHostingType/skip - data from localStorage');
          return;
        }

        // If we get here, we don't have valid hostingType data in localStorage, so fetch from API
        logStoreAction('ConfigStore', 'getHostingType/fetching from API - no data in localStorage');
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