import { StateCreator } from '@/lib/zustand';
import type { ConfigStore, ConfigActions } from '../types';
import { useLoadingStore } from '@/stores/loadingStore';

export const createInitializeConfigAction: StateCreator<ConfigStore, [], [], Pick<ConfigActions, 'initializeConfig'>> = (set, get, api) => ({
  initializeConfig: async (autoLoad = true, all = false) => {
    if (!autoLoad) {
      return;
    }

    const { showLoading, hideLoading } = useLoadingStore.getState();
    const { getConfig, loadAvailableLLMProviders, loadAvailableRepos } = get();

    showLoading('Loading configuration...', 'Please wait while we load your settings');

    try {

      if (all) {
        await Promise.all([
          getConfig(all),
          loadAvailableLLMProviders(),
          loadAvailableRepos(),
        ]);
      } else {
        await Promise.all([
          getConfig(all),
        ]);
      }
    } catch (err) {
      console.error('Failed to initialize config:', err);
      // Optionally, set an error state in the configStore here
    } finally {
      hideLoading();
    }
  },
});