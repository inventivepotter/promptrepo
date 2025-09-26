// Config Store - Main store file
import { create } from 'zustand';
import { immer } from '@/lib/zustand';
import { initialConfigState } from './state';
import { createConfigActions } from './actions';
import type { ConfigStore } from './types';

// Create the config store
export const useConfigStore = create<ConfigStore>()(
  immer((set, get, ...rest) => {
    // Return initial state combined with actions
    return {
      ...initialConfigState,
      ...createConfigActions(set, get, ...rest),
    };
  })
);