// Set loading config action
import type { StateCreator } from '@/lib/zustand';
import type { ConfigStore, ConfigActions } from '../types';

export const createSetLoadingConfigAction: StateCreator<
  ConfigStore,
  [],
  [],
  Pick<ConfigActions, 'setLoadingConfig'>
> = (set) => ({
  setLoadingConfig: (loading: boolean) => {
    set((draft) => {
      draft.isLoadingConfig = loading;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'config/setLoadingConfig');
  },
});