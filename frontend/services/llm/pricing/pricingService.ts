import type { PricingData, ModelPricing, CostCalculation, TokenUsage } from '@/types/Pricing';
import {
  fetchPricingData,
  getPricingData,
  getModelPricing,
  searchModels as searchModelsFromStore,
  getAllModels as getAllModelsFromStore
} from '@/stores/pricingStore';

export class PricingService {
  private pricingData: PricingData | null = null;
  private lastFetched: Date | null = null;
  private readonly cacheExpiry = 1000 * 60 * 60; // 1 hour cache

  async downloadPricingData(): Promise<PricingData> {
    // Use the store's fetchPricingData function
    const data = await fetchPricingData(true); // Force refresh
    this.pricingData = data;
    this.lastFetched = new Date();
    return data;
  }

  async getPricingData(): Promise<PricingData> {
    // Check if we have fresh data in memory
    if (this.pricingData && this.lastFetched) {
      const age = Date.now() - this.lastFetched.getTime();
      if (age < this.cacheExpiry) {
        return this.pricingData;
      }
    }

    // Try to get data from store
    const dataFromStore = getPricingData(this.cacheExpiry);
    if (dataFromStore) {
      this.pricingData = dataFromStore;
      this.lastFetched = new Date(Date.now() - (this.cacheExpiry / 2)); // Set a reasonable timestamp
      return dataFromStore;
    }

    // Fetch fresh data
    const freshData = await fetchPricingData();
    this.pricingData = freshData;
    this.lastFetched = new Date();
    return freshData;
  }

  calculateCost(modelName: string, tokenUsage: TokenUsage): CostCalculation | null {
    // Try to get model pricing from store
    const modelPricing = getModelPricing(modelName);
    if (!modelPricing) {
      return null;
    }

    const inputCost = tokenUsage.inputTokens * modelPricing.input_cost_per_token;
    const outputCost = tokenUsage.outputTokens * modelPricing.output_cost_per_token;
    const reasoningCost = (tokenUsage.reasoningTokens || 0) * (modelPricing.output_cost_per_reasoning_token || modelPricing.output_cost_per_token);
    const totalCost = inputCost + outputCost + reasoningCost;

    return {
      inputTokens: tokenUsage.inputTokens,
      outputTokens: tokenUsage.outputTokens,
      inputCost,
      outputCost: outputCost + reasoningCost,
      totalCost,
      modelName,
      provider: modelPricing.litellm_provider
    };
  }

  getModelInfo(modelName: string): ModelPricing | null {
    // Use the store's getModelPricing function
    return getModelPricing(modelName);
  }

  searchModels(query: string): Array<{ name: string; pricing: ModelPricing }> {
    // Use the store's searchModels function
    return searchModelsFromStore(query);
  }

  getAllModels(): Array<{ name: string; pricing: ModelPricing }> {
    // Use the store's getAllModels function
    return getAllModelsFromStore();
  }

  downloadPricingFile() {
    if (!this.pricingData) {
      throw new Error('No pricing data available to download');
    }

    const dataStr = JSON.stringify(this.pricingData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `litellm_pricing_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    URL.revokeObjectURL(url);
  }

  formatCost(cost: number): string {
    if (cost === 0) return '$0.00';
    if (cost < 0.001) return `$${cost.toExponential(2)}`;
    return `$${cost.toFixed(4)}`;
  }
}

// Singleton instance
export const pricingService = new PricingService();
