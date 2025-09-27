// Set available providers action
import type { StateCreator } from '@/lib/zustand';
import type { ConfigStore, BasicProviderInfo } from '../types';

export const createSetAvailableProvidersAction: StateCreator<
  ConfigStore,
  [],
  [],
  { setAvailableProviders: (providers: BasicProviderInfo[]) => void }
> = (set) => {
  return {
    setAvailableProviders: (providers: BasicProviderInfo[]) => {
      set((draft) => {
        draft.availableLLMProviders = providers;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/setAvailableProviders');
    },
  };
};