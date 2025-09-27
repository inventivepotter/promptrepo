// Storage configuration for config store
import { createLocalStorage } from '@/lib/zustand';
import type { ConfigStore } from './types';

/**
 * Storage configuration using centralized utilities from lib/zustand
 * Benefits:
 * - Consistent storage configuration across the app
 * - Centralized storage utilities
 * - Built-in error handling and SSR support
 * - Uses localStorage for persistence across browser sessions
 */
export const configPersistConfig = {
  ...createLocalStorage('config-store'),
  // Only persist essential config data
  partialize: (state: ConfigStore) => ({
    availableProviders: state.availableLLMProviders,
    availableRepos: state.availableRepos,
    hostingType: state.hostingType,
    config: state.config,
  }),
  // Set to true if you want to manually hydrate
  skipHydration: false,
  // Version for migration support
  version: 1,
  // Migration function for future schema changes
  migrate: (persistedState: unknown, version: number) => {
    if (version === 0) {
      // Handle migration from version 0 to 1
      // Example: rename old fields, transform data structure
    }
    return persistedState;
  },
};