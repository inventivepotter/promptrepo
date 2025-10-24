import type { PricingData } from '@/types/Pricing';

export interface PricingState {
  // Data
  pricingData: PricingData | null;
  
  // UI State
  isLoading: boolean;
  isFetching: boolean;
  error: string | null;
  
  // Cache management
  lastFetched: number | null;
  cacheExpiry: number; // 24 hours in milliseconds
}

export type ModelPricingInfo = {
  promptCost: number;
  completionCost: number;
  reasoningCost?: number;
};

export interface PricingActions {
  // Data fetching
  fetchPricingData: (forceRefresh?: boolean) => Promise<PricingData>;
  getPricingData: (maxAge?: number) => PricingData | null;
  
  // Model queries
  getModelPricing: (modelName: string) => ModelPricingInfo | null;
  searchModels: (query: string) => Array<{ name: string; pricing: ModelPricingInfo }>;
  getAllModels: () => Array<{ name: string; pricing: ModelPricingInfo }>;
  
  // Utilities
  downloadPricingFile: () => void;
  
  // State management
  setError: (error: string | null) => void;
  clearError: () => void;
  reset: () => void;
}

export interface PricingStore extends PricingState, PricingActions {}