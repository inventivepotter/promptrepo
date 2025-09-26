// Storage configuration for auth store
import { createSessionStorage } from '@/lib/zustand';
import type { AuthStore } from './types';

/**
 * Storage configuration using centralized utilities from lib/zustand
 * Benefits:
 * - Consistent storage configuration across the app
 * - Centralized storage utilities
 * - Built-in error handling and SSR support
 */
export const authPersistConfig = {
  ...createSessionStorage('auth-store'),
  // Only persist essential auth data
  partialize: (state: AuthStore) => ({
    user: state.user,
    isAuthenticated: state.isAuthenticated,
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
