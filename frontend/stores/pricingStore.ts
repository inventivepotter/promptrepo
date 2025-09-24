import { localStorage } from "@/lib/localStorage";
import { LOCAL_STORAGE_KEYS } from "@/utils/localStorageConstants";
import type { ModelPricing, PricingData } from "@/app/(prompts)/_types/PricingTypes";

// Use the centralized storage keys
const STORE_NAME = LOCAL_STORAGE_KEYS;

// Interface for cached pricing data with timestamp
interface CachedPricingData {
  data: PricingData;
  timestamp: number;
}

/**
 * Store pricing data to localStorage with timestamp
 * @param pricingData - Pricing data to store
 */
export const setPricingData = (pricingData: PricingData): void => {
  localStorage.set(STORE_NAME.PRICING_DATA, {
    data: pricingData,
    timestamp: Date.now()
  });
};

/**
 * Get pricing data from localStorage with cache age checking
 * @param maxAge - Maximum age of cache in milliseconds (default: 24 hours)
 * @returns Pricing data if valid and not expired, null otherwise
 */
export const getPricingData = (maxAge: number = 24 * 60 * 60 * 1000): PricingData | null => {
  const cached = localStorage.get<CachedPricingData>(STORE_NAME.PRICING_DATA);
  if (!cached) return null;
  
  try {
    // Check if cache is expired
    const age = Date.now() - cached.timestamp;
    if (age > maxAge) {
      clearPricingData();
      return null;
    }
    
    // Validate the data structure
    const isValidPricingData = typeof cached.data === 'object' && cached.data !== null;
    if (!isValidPricingData) {
      console.warn('Invalid pricing data structure found in localStorage');
      clearPricingData();
      return null;
    }
    
    return cached.data;
  } catch (error) {
    console.error('Failed to parse cached pricing data:', error);
    clearPricingData();
    return null;
  }
};

/**
 * Clear pricing data from localStorage
 */
export const clearPricingData = (): void => {
  localStorage.clear(STORE_NAME.PRICING_DATA);
};

/**
 * Transform full pricing data to extract only essential fields
 * @param fullData - Full pricing data from API
 * @returns Transformed pricing data with only essential fields
 */
export const transformPricingData = (fullData: Record<string, unknown>): PricingData => {
  const essentialData: PricingData = {};
  
  for (const [modelName, modelData] of Object.entries(fullData)) {
    const data = modelData as Record<string, unknown>;
    
    // Validate required fields
    if (typeof data.input_cost_per_token === 'number' &&
        typeof data.output_cost_per_token === 'number' &&
        typeof data.litellm_provider === 'string') {
      
      essentialData[modelName] = {
        input_cost_per_token: data.input_cost_per_token,
        output_cost_per_token: data.output_cost_per_token,
        output_cost_per_reasoning_token: typeof data.output_cost_per_reasoning_token === 'number' 
          ? data.output_cost_per_reasoning_token 
          : undefined,
        litellm_provider: data.litellm_provider
      };
    }
  }
  
  return essentialData;
};

/**
 * Fetch pricing data from remote source with cache-first strategy
 * @param forceRefresh - Whether to force refresh from remote
 * @returns Promise resolving to pricing data
 */
export const fetchPricingData = async (forceRefresh: boolean = false): Promise<PricingData> => {
  const LITELLM_PRICING_URL = 'https://raw.githubusercontent.com/BerriAI/litellm/refs/heads/main/model_prices_and_context_window.json';
  
  // Try to get from cache first (unless forcing refresh)
  if (!forceRefresh) {
    const cachedData = getPricingData();
    if (cachedData) {
      return cachedData;
    }
  }
  
  try {
    const response = await fetch(LITELLM_PRICING_URL);
    if (!response.ok) {
      throw new Error(`Failed to fetch pricing data: ${response.statusText}`);
    }
    
    const fullData = await response.json() as Record<string, unknown>;
    const essentialData = transformPricingData(fullData);
    
    // Store the transformed data
    setPricingData(essentialData);
    
    return essentialData;
  } catch (error) {
    console.error('Failed to fetch pricing data:', error);
    
    // Try to use cached data as fallback
    const cachedData = getPricingData();
    if (cachedData) {
      return cachedData;
    }
    
    throw error;
  }
};

/**
 * Get model pricing information for a specific model
 * @param modelName - Name of the model to get pricing for
 * @returns Model pricing information if found, null otherwise
 */
export const getModelPricing = (modelName: string): ModelPricing | null => {
  const pricingData = getPricingData();
  if (!pricingData || !pricingData[modelName]) {
    return null;
  }
  return pricingData[modelName];
};

/**
 * Search for models by name or provider
 * @param query - Search query string
 * @returns Array of matching models with pricing information
 */
export const searchModels = (query: string): Array<{ name: string; pricing: ModelPricing }> => {
  const pricingData = getPricingData();
  if (!pricingData) {
    return [];
  }
  
  const results: Array<{ name: string; pricing: ModelPricing }> = [];
  const lowerQuery = query.toLowerCase();
  
  for (const [modelName, pricing] of Object.entries(pricingData)) {
    if (modelName.toLowerCase().includes(lowerQuery) ||
        pricing.litellm_provider.toLowerCase().includes(lowerQuery)) {
      results.push({ name: modelName, pricing });
    }
  }
  
  return results.sort((a, b) => a.name.localeCompare(b.name));
};

/**
 * Get all available models with pricing information
 * @returns Array of all models with pricing information, sorted by name
 */
export const getAllModels = (): Array<{ name: string; pricing: ModelPricing }> => {
  const pricingData = getPricingData();
  if (!pricingData) {
    return [];
  }
  
  return Object.entries(pricingData).map(([name, pricing]) => ({
    name,
    pricing
  })).sort((a, b) => a.name.localeCompare(b.name));
};

/**
 * Check if pricing data exists in storage and is not expired
 * @returns Boolean indicating if valid pricing data exists
 */
export const hasValidPricingData = (): boolean => {
  return getPricingData() !== null;
};

/**
 * Get the timestamp of when the pricing data was last stored
 * @returns Timestamp if data exists, null otherwise
 */
export const getPricingDataTimestamp = (): number | null => {
  const cached = localStorage.get<CachedPricingData>(STORE_NAME.PRICING_DATA);
  return cached?.timestamp || null;
};

/**
 * Get the age of the cached pricing data in milliseconds
 * @returns Age in milliseconds if data exists, null otherwise
 */
export const getPricingDataAge = (): number | null => {
  const timestamp = getPricingDataTimestamp();
  if (!timestamp) return null;
  return Date.now() - timestamp;
};

// Backward compatibility exports
export const storePricingData = setPricingData;
export const getPricingDataFromStorage = getPricingData;
export const clearPricingDataFromStorage = clearPricingData;