import { usePricingStore } from './store';
import {
  selectPricingData,
  selectLastFetched,
  selectIsLoading,
  selectIsFetching,
  selectIsProcessing,
  selectError,
  selectCacheExpiry,
  selectIsCacheStale,
  selectModelPricing,
  selectAllModels,
  selectSearchModels,
  selectModelCount,
  selectHasPricingData,
  selectCacheAge,
} from './selectors';

// Data Hooks
export const usePricingData = () => usePricingStore(selectPricingData);
export const useLastFetched = () => usePricingStore(selectLastFetched);

// Loading State Hooks
export const useIsLoading = () => usePricingStore(selectIsLoading);
export const useIsFetching = () => usePricingStore(selectIsFetching);
export const useIsProcessing = () => usePricingStore(selectIsProcessing);

// Error Hook
export const usePricingError = () => usePricingStore(selectError);

// Cache Hooks
export const useCacheExpiry = () => usePricingStore(selectCacheExpiry);
export const useIsCacheStale = () => usePricingStore(selectIsCacheStale);
export const useCacheAge = () => usePricingStore(selectCacheAge);

// Model Hooks
export const useModelPricing = (modelName: string) => 
  usePricingStore(selectModelPricing(modelName));

export const useAllModels = () => usePricingStore(selectAllModels);

export const useSearchModels = (query: string) => 
  usePricingStore(selectSearchModels(query));

// Computed Hooks
export const useModelCount = () => usePricingStore(selectModelCount);
export const useHasPricingData = () => usePricingStore(selectHasPricingData);

// Action Hooks
export const usePricingActions = () => {
  const store = usePricingStore();
  
  return {
    fetchPricingData: store.fetchPricingData,
    getPricingData: store.getPricingData,
    getModelPricing: store.getModelPricing,
    searchModels: store.searchModels,
    getAllModels: store.getAllModels,
    downloadPricingFile: store.downloadPricingFile,
    setError: store.setError,
    clearError: store.clearError,
    reset: store.reset,
  };
};

// Convenience hook that returns everything
export const usePricingStoreState = () => {
  const pricingData = usePricingData();
  const isLoading = useIsLoading();
  const isFetching = useIsFetching();
  const isProcessing = useIsProcessing();
  const error = usePricingError();
  const isCacheStale = useIsCacheStale();
  const hasPricingData = useHasPricingData();
  const actions = usePricingActions();
  
  return {
    // Data
    pricingData,
    
    // Loading States
    isLoading,
    isFetching,
    isProcessing,
    
    // Error
    error,
    
    // Cache
    isCacheStale,
    hasPricingData,
    
    // Actions
    ...actions,
  };
};