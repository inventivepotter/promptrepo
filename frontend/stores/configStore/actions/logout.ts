// Logout action to clear config
import type { StateCreator } from '@/lib/zustand';
import { logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';
import { initialConfigState } from '../state';
import { usePromptStore } from '@/stores/promptStore/store';

export const createLogoutAction: StateCreator<
  ConfigStore,
  [],
  [],
  { logout: () => void }
> = (set) => {
  return {
    logout: () => {
      logStoreAction('ConfigStore', 'logout', {});
      
      // Clear config store
      set((draft) => {
        if (draft.config.llm_configs) {
          draft.config.llm_configs = initialConfigState.config.llm_configs;
        }
        if (draft.config.repo_configs) {
          draft.config.repo_configs = initialConfigState.config.repo_configs;
        }
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/logout');
      
      // Invalidate prompt cache on logout
      usePromptStore.getState().invalidateCache();
      console.log('Cleared config and prompt caches on logout');
    },
  };
};