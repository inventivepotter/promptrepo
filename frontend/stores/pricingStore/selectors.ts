// Selectors for Pricing Store
import type { PricingStore } from './types';
import type { ModelPricing } from '@/types/Pricing';

// Data Selectors
export const selectPricingData = (state: PricingStore) => state.pricingData;
export const selectLastFetched = (state: PricingStore) => state.lastFetched;

// Loading State Selectors
export const selectIsLoading = (state: PricingStore) => state.isLoading;
export const selectIsFetching = (state: PricingStore) => state.isFetching;
export const selectIsProcessing = (state: PricingStore) => state.isLoading || state.isFetching;

// Error Selector
export const selectError = (state: PricingStore) => state.error;

// Cache Selectors
export const selectCacheExpiry = (state: PricingStore) => state.cacheExpiry;
export const selectIsCacheStale = (state: PricingStore) => {
  if (!state.lastFetched) return true;
  const age = Date.now() - state.lastFetched;
  return age > state.cacheExpiry;
};

// Model Selectors (using higher-order selectors)
export const selectModelPricing = (modelName: string) => (state: PricingStore): ModelPricing | null => {
  return state.getModelPricing(modelName);
};

export const selectAllModels = (state: PricingStore) => {
  return state.getAllModels();
};

export const selectSearchModels = (query: string) => (state: PricingStore) => {
  return state.searchModels(query);
};

// Computed Selectors
export const selectModelCount = (state: PricingStore) => {
  if (!state.pricingData) return 0;
  return Object.keys(state.pricingData).length;
};

export const selectHasPricingData = (state: PricingStore) => {
  return state.pricingData !== null;
};

export const selectCacheAge = (state: PricingStore) => {
  if (!state.lastFetched) return null;
  return Date.now() - state.lastFetched;
};