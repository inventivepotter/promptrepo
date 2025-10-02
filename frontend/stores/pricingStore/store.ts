// Main pricing store implementation
import { create } from 'zustand';
import { devtools, persist, immer } from '@/lib/zustand';
import { createPricingActions } from './actions';
import { initialPricingState } from './state';
import { pricingPersistConfig } from './storage';
import type { PricingStore } from './types';

// Create the pricing store with middleware
export const usePricingStore = create<PricingStore>()(
  devtools(
    persist(
      immer((set, get, api) => ({
        // Initial state
        ...initialPricingState,
        
        // Actions
        ...createPricingActions(set, get),
      })),
      pricingPersistConfig
    ),
    {
      name: 'pricing-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

// Export the store instance for direct access if needed
export default usePricingStore;