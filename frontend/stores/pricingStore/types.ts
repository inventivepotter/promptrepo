import type { PricingData, ModelPricing } from '@/types/Pricing';

export interface PricingState {
  // Data
  pricingData: PricingData | null;
  
  // UI State
  isLoading: boolean;
  isFetching: boolean;
  error: string | null;
  
  // Cache management
  lastFetched: number | null;
  cacheExpiry: number; // 1 hour in milliseconds
}

export interface PricingActions {
  // Data fetching
  fetchPricingData: (forceRefresh?: boolean) => Promise<PricingData>;
  getPricingData: (maxAge?: number) => PricingData | null;
  
  // Model queries
  getModelPricing: (modelName: string) => ModelPricing | null;
  searchModels: (query: string) => Array<{ name: string; pricing: ModelPricing }>;
  getAllModels: () => Array<{ name: string; pricing: ModelPricing }>;
  
  // Utilities
  downloadPricingFile: () => void;
  
  // State management
  setError: (error: string | null) => void;
  clearError: () => void;
  reset: () => void;
}

export interface PricingStore extends PricingState, PricingActions {}