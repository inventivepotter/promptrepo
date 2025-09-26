// Set error action
import type { StateCreator } from '@/lib/zustand';
import type { ConfigStore } from '../types';

export const createSetErrorAction: StateCreator<
  ConfigStore,
  [],
  [],
  { setError: (error: string | null) => void }
> = (set) => {
  return {
    setError: (error: string | null) => {
      set((draft) => {
        draft.error = error;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'config/setError');
    },
  };
};