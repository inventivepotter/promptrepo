// Storage configuration for prompt store
import { createLocalStorage } from '@/lib/zustand';
import type { PromptStore } from './types';

/**
 * Storage configuration using centralized utilities from lib/zustand
 * Benefits:
 * - Consistent storage configuration across the app
 * - Centralized storage utilities
 * - Built-in error handling and SSR support
 * - Uses localStorage for persistence across browser sessions
 */
export const promptPersistConfig = {
  ...createLocalStorage('prompt-store'),
  // Only persist essential prompt data
  partialize: (state: PromptStore) => ({
    prompts: state.prompts,
    filters: state.filters,
    pagination: state.pagination,
    currentPrompt: state.currentPrompt,
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