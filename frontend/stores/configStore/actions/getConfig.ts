// Get config action
import type { StateCreator } from '@/lib/zustand';
import { ConfigService } from '@/services/config/configService';
import { handleStoreError, logStoreAction } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createGetConfigAction: StateCreator<
  ConfigStore,
  [],
  [],
  { getConfig: (all?: boolean) => Promise<void> }
> = (set, get) => {
  return {
    getConfig: async (all = false) => {
      const actionName = all ? 'getAllConfigs' : 'getConfig';
      logStoreAction('ConfigStore', actionName);
      
      set((draft) => {
        draft.error = null;
        draft.isLoadingConfig = true;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, `config/${actionName}/start`);

      try {
        // Check if we already have config data (from localStorage hydration)
        const currentState = get();
        
        // Check if we have a valid config that's not just the default initial state
        // We need to check if the config has been fetched from the API before
        let hasValidConfig = false;
        
        if (currentState.config && currentState.config.hosting_config && currentState.config.hosting_config.type) {
          // Basic config validation passed
          // For organization hosting, check OAuth configs
          if (currentState.config.hosting_config.type === "organization") {
            hasValidConfig = !!(currentState.config.oauth_configs && currentState.config.oauth_configs.length > 0);
          } else {
            // For individual hosting, basic config is enough
            hasValidConfig = true;
          }
          
          // If 'all' parameter is true, also check LLM and repo configs
          if (all && hasValidConfig) {
            const hasLLMConfigs = !!(currentState.config.llm_configs && currentState.config.llm_configs.length > 0);
            const hasRepoConfigs = !!(currentState.config.repo_configs && currentState.config.repo_configs.length > 0);
            hasValidConfig = hasLLMConfigs || hasRepoConfigs;
          }
        }
          
        if (hasValidConfig) {
          // We have valid config data, no need to call API
          logStoreAction('ConfigStore', `${actionName}/skip - data from localStorage`);
          set((draft) => {
            draft.isLoadingConfig = false;
          // @ts-expect-error - Immer middleware supports 3 params
          }, false, `config/${actionName}/skip`);
          return;
        }

        // If we get here, we don't have valid config data, so fetch from API
        logStoreAction('ConfigStore', `${actionName}/fetching from API`);
        const config = await ConfigService.getConfig();
        
        set((draft) => {
          draft.config = config;
          draft.isLoadingConfig = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, `config/${actionName}/success`);
      } catch (error) {
        const storeError = handleStoreError(error, actionName);
        console.error(`${actionName} error:`, error);
        
        set((draft) => {
          draft.error = storeError.message;
          draft.isLoadingConfig = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, `config/${actionName}/error`);
        
        throw error;
      } finally {
        set((draft) => {
          draft.isLoadingConfig = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, `config/${actionName}/complete`);
      }
    },
  };
};