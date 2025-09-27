// Config Store - Main store file
import { create } from 'zustand';
import { devtools, persist, immer } from '@/lib/zustand';
import { initialConfigState } from './state';
import { createConfigActions } from './actions';
import { configPersistConfig } from './storage';
import type { ConfigStore } from './types';

// Create the config store with middleware
export const useConfigStore = create<ConfigStore>()(
  devtools(
    persist(
      immer((set, get, ...rest) => {
        // Return initial state combined with actions
        return {
          ...initialConfigState,
          ...createConfigActions(set, get, ...rest),
        };
      }),
      configPersistConfig
    ),
    {
      name: 'config-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);