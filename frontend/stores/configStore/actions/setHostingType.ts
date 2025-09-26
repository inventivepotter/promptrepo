// Set hosting type action
import type { StateCreator } from '@/lib/zustand';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createSetHostingTypeAction: StateCreator<
  ConfigStore,
  [],
  [],
  { setHostingType: (hostingType: string) => void }
> = (set) => {
  return {
    setHostingType: (hostingType: string) => {
      logStoreAction('ConfigStore', 'setHostingType', { hostingType });
      
      try {
        set((draft) => {
          draft.hostingType = hostingType;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setHostingType');
      } catch (error) {
        const storeError = handleStoreError(error, 'setHostingType');
        console.error('Set hosting type error:', error);
        
        set((draft) => {
          draft.error = storeError.message;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'config/setHostingType/error');
        
        throw error;
      }
    },
  };
};