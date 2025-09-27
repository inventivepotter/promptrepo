import type { StateCreator } from '@/lib/zustand';
import type { ConfigStore, ConfigActions } from '../types';

export const createLLMFormActions: StateCreator<ConfigStore, [], [], Pick<ConfigActions, 'setProviderSearchValue' | 'setModelSearchValue'>> = (set) => ({
  setProviderSearchValue: (value) => set({ providerSearchValue: value }),
  setModelSearchValue: (value) => set({ modelSearchValue: value }),
});