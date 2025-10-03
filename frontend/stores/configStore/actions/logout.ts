// Logout action to clear config
import type { StateCreator } from '@/lib/zustand';
import { logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';
import { initialConfigState } from '../state';

export const createLogoutAction: StateCreator<
  ConfigStore,
  [],
  [],
  { logout: () => void }
> = (set) => {
  return {
    logout: () => {
      logStoreAction('ConfigStore', 'logout', {});
      
      set((draft) => {
        if (draft.config.llm_configs) {
          draft.config.llm_configs = initialConfigState.config.llm_configs;
        }
        if (draft.config.repo_configs) {
          draft.config.repo_configs = initialConfigState.config.repo_configs;
        }
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/logout');
    },
  };
};