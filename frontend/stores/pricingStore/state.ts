// Initial state for Pricing Store
import type { PricingState } from './types';

export const initialPricingState: PricingState = {
  // Data
  pricingData: null,
  
  // UI State
  isLoading: false,
  isFetching: false,
  error: null,
  
  // Cache management
  lastFetched: null,
  cacheExpiry: 1000 * 60 * 60, // 1 hour
};