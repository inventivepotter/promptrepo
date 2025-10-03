import type { PricingData, ModelPricing, CostCalculation, TokenUsage } from '@/types/Pricing';

const PRICING_DATA_URL = 'https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json';

export class PricingService {
  private pricingData: PricingData | null = null;
  private lastFetched: Date | null = null;
  private readonly cacheExpiry = 1000 * 60 * 60; // 1 hour cache
  private readonly localStorageKey = 'litellm_pricing_data';
  private readonly localStorageTimestampKey = 'litellm_pricing_timestamp';

  private async fetchPricingDataFromSource(): Promise<PricingData> {
    const response = await fetch(PRICING_DATA_URL);
    if (!response.ok) {
      throw new Error(`Failed to fetch pricing data: ${response.statusText}`);
    }
    return await response.json();
  }

  private savePricingDataToLocalStorage(data: PricingData): void {
    try {
      localStorage.setItem(this.localStorageKey, JSON.stringify(data));
      localStorage.setItem(this.localStorageTimestampKey, Date.now().toString());
    } catch (error) {
      console.warn('Failed to save pricing data to localStorage:', error);
    }
  }

  private loadPricingDataFromLocalStorage(): PricingData | null {
    try {
      const data = localStorage.getItem(this.localStorageKey);
      const timestamp = localStorage.getItem(this.localStorageTimestampKey);
      
      if (!data || !timestamp) {
        return null;
      }

      const age = Date.now() - parseInt(timestamp, 10);
      if (age > this.cacheExpiry) {
        return null;
      }

      return JSON.parse(data);
    } catch (error) {
      console.warn('Failed to load pricing data from localStorage:', error);
      return null;
    }
  }

  async downloadPricingData(): Promise<PricingData> {
    const data = await this.fetchPricingDataFromSource();
    this.pricingData = data;
    this.lastFetched = new Date();
    this.savePricingDataToLocalStorage(data);
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

    // Try to get data from localStorage
    const dataFromStorage = this.loadPricingDataFromLocalStorage();
    if (dataFromStorage) {
      this.pricingData = dataFromStorage;
      this.lastFetched = new Date();
      return dataFromStorage;
    }

    // Fetch fresh data
    const freshData = await this.fetchPricingDataFromSource();
    this.pricingData = freshData;
    this.lastFetched = new Date();
    this.savePricingDataToLocalStorage(freshData);
    return freshData;
  }

  private getModelPricing(modelName: string): ModelPricing | null {
    if (!this.pricingData) {
      return null;
    }
    return this.pricingData[modelName] || null;
  }

  calculateCost(modelName: string, tokenUsage: TokenUsage): CostCalculation | null {
    const modelPricing = this.getModelPricing(modelName);
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
    return this.getModelPricing(modelName);
  }

  searchModels(query: string): Array<{ name: string; pricing: ModelPricing }> {
    if (!this.pricingData) {
      return [];
    }

    const lowerQuery = query.toLowerCase();
    return Object.entries(this.pricingData)
      .filter(([name]) => name.toLowerCase().includes(lowerQuery))
      .map(([name, pricing]) => ({ name, pricing }));
  }

  getAllModels(): Array<{ name: string; pricing: ModelPricing }> {
    if (!this.pricingData) {
      return [];
    }

    return Object.entries(this.pricingData).map(([name, pricing]) => ({ name, pricing }));
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
