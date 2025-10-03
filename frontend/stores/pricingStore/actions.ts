// Actions for Pricing Store
import type { StateCreator } from 'zustand';
import type { PricingStore, PricingActions } from './types';
import type { PricingData } from '@/types/Pricing';
import { pricingService } from '@/services/llm/pricing/pricingService';

export const createPricingActions = (
  set: Parameters<StateCreator<PricingStore>>[0],
  get: Parameters<StateCreator<PricingStore>>[1]
): PricingActions => ({
  fetchPricingData: async (forceRefresh = false) => {
    set({ isFetching: true, error: null });

    try {
      let data: PricingData;
      
      if (forceRefresh) {
        data = await pricingService.downloadPricingData();
      } else {
        data = await pricingService.getPricingData();
      }
      
      set({
        pricingData: data,
        lastFetched: Date.now(),
        isFetching: false,
        error: null,
      });
      
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to fetch pricing data';
      set({
        error: errorMessage,
        isFetching: false,
      });
      throw error;
    }
  },

  getPricingData: (maxAge?: number) => {
    const state = get();
    
    if (!state.pricingData || !state.lastFetched) {
      return null;
    }

    const age = Date.now() - state.lastFetched;
    const ageLimit = maxAge ?? state.cacheExpiry;
    
    if (age > ageLimit) {
      return null;
    }

    return state.pricingData;
  },

  getModelPricing: (modelName: string) => {
    const state = get();
    if (!state.pricingData) {
      return null;
    }
    return state.pricingData[modelName] || null;
  },

  searchModels: (query: string) => {
    const state = get();
    if (!state.pricingData) {
      return [];
    }

    const lowerQuery = query.toLowerCase();
    return Object.entries(state.pricingData)
      .filter(([name]) => name.toLowerCase().includes(lowerQuery))
      .map(([name, pricing]) => ({ name, pricing }));
  },

  getAllModels: () => {
    const state = get();
    if (!state.pricingData) {
      return [];
    }

    return Object.entries(state.pricingData).map(([name, pricing]) => ({ name, pricing }));
  },

  downloadPricingFile: () => {
    const state = get();
    if (!state.pricingData) {
      throw new Error('No pricing data available to download');
    }

    const dataStr = JSON.stringify(state.pricingData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `litellm_pricing_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  },

  setError: (error: string | null) => {
    set({ error });
  },

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set({
      pricingData: null,
      isLoading: false,
      isFetching: false,
      error: null,
      lastFetched: null,
    });
  },
});