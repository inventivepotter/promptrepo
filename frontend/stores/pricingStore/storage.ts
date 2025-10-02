// Storage configuration for pricing store
import { createIndexedDBStorage } from '@/lib/zustand';
import type { PricingStore } from './types';

/**
 * Storage configuration using IndexedDB for better performance with larger datasets
 * Benefits:
 * - Much larger storage capacity than localStorage (GBs vs 5-10MB)
 * - Better performance for large datasets
 * - Asynchronous operations don't block the main thread
 * - Built-in error handling and SSR support
 */
export const pricingPersistConfig = {
  ...createIndexedDBStorage('pricing-store'),
  // Only persist essential pricing data and cache metadata
  partialize: (state: PricingStore) => ({
    pricingData: state.pricingData,
    lastFetched: state.lastFetched,
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