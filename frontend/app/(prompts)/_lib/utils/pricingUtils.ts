import { PricingData, ModelPricing, CostCalculation, TokenUsage } from '../../_types/PricingTypes';

const LITELLM_PRICING_URL = 'https://raw.githubusercontent.com/BerriAI/litellm/refs/heads/main/model_prices_and_context_window.json';

export class PricingService {
  private pricingData: PricingData | null = null;
  private lastFetched: Date | null = null;
  private readonly cacheExpiry = 1000 * 60 * 60; // 1 hour cache

  async downloadPricingData(): Promise<PricingData> {
    try {
      const response = await fetch(LITELLM_PRICING_URL);
      if (!response.ok) {
        throw new Error(`Failed to fetch pricing data: ${response.statusText}`);
      }
      
      const fullData = await response.json();
      
      // Extract only the fields we need
      const essentialData: PricingData = {};
      for (const [modelName, modelData] of Object.entries(fullData)) {
        const data = modelData as Record<string, unknown>;
        if (typeof data.input_cost_per_token === 'number' &&
            typeof data.output_cost_per_token === 'number' &&
            typeof data.litellm_provider === 'string') {
          essentialData[modelName] = {
            input_cost_per_token: data.input_cost_per_token,
            output_cost_per_token: data.output_cost_per_token,
            output_cost_per_reasoning_token: typeof data.output_cost_per_reasoning_token === 'number' ? data.output_cost_per_reasoning_token : undefined,
            litellm_provider: data.litellm_provider
          };
        }
      }
      
      this.pricingData = essentialData;
      this.lastFetched = new Date();
      
      // Cache only the essential data
      localStorage.setItem('litellm_pricing_essential', JSON.stringify({
        data: essentialData,
        timestamp: this.lastFetched.getTime()
      }));
      
      return essentialData;
    } catch (error) {
      console.error('Failed to download pricing data:', error);
      
      // Try to use cached data as fallback
      const cached = this.getCachedData();
      if (cached) {
        return cached;
      }
      
      throw error;
    }
  }

  private getCachedData(): PricingData | null {
    try {
      const cached = localStorage.getItem('litellm_pricing_essential');
      if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        const age = Date.now() - timestamp;
        
        // Use cached data if it's less than 24 hours old
        if (age < 24 * 60 * 60 * 1000) {
          this.pricingData = data;
          return data;
        }
      }
    } catch (error) {
      console.warn('Failed to parse cached pricing data:', error);
    }
    return null;
  }

  async getPricingData(): Promise<PricingData> {
    // Check if we have fresh data
    if (this.pricingData && this.lastFetched) {
      const age = Date.now() - this.lastFetched.getTime();
      if (age < this.cacheExpiry) {
        return this.pricingData;
      }
    }

    // Try cached data first
    const cached = this.getCachedData();
    if (cached) {
      return cached;
    }

    // Download fresh data
    return await this.downloadPricingData();
  }

  calculateCost(modelName: string, tokenUsage: TokenUsage): CostCalculation | null {
    if (!this.pricingData || !this.pricingData[modelName]) {
      return null;
    }

    const modelPricing = this.pricingData[modelName];
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
    if (!this.pricingData || !this.pricingData[modelName]) {
      return null;
    }
    return this.pricingData[modelName];
  }

  searchModels(query: string): Array<{ name: string; pricing: ModelPricing }> {
    if (!this.pricingData) {
      return [];
    }

    const results: Array<{ name: string; pricing: ModelPricing }> = [];
    const lowerQuery = query.toLowerCase();

    for (const [modelName, pricing] of Object.entries(this.pricingData)) {
      if (modelName.toLowerCase().includes(lowerQuery) || 
          pricing.litellm_provider.toLowerCase().includes(lowerQuery)) {
        results.push({ name: modelName, pricing });
      }
    }

    return results.sort((a, b) => a.name.localeCompare(b.name));
  }

  getAllModels(): Array<{ name: string; pricing: ModelPricing }> {
    if (!this.pricingData) {
      return [];
    }

    return Object.entries(this.pricingData).map(([name, pricing]) => ({
      name,
      pricing
    })).sort((a, b) => a.name.localeCompare(b.name));
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
}

// Singleton instance
export const pricingService = new PricingService();

// Utility functions
export function formatCost(cost: number): string {
  if (cost === 0) return '$0.00';
  if (cost < 0.001) return `$${cost.toExponential(2)}`;
  return `$${cost.toFixed(4)}`;
}

export function formatTokens(tokens: number): string {
  if (tokens < 1000) return tokens.toString();
  if (tokens < 1000000) return `${(tokens / 1000).toFixed(1)}K`;
  return `${(tokens / 1000000).toFixed(1)}M`;
}