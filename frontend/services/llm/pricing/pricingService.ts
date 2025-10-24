import type { PricingData, OpenRouterResponse, CostCalculation, TokenUsage } from '@/types/Pricing';

const PRICING_DATA_URL = 'https://openrouter.ai/api/v1/models';

export class PricingService {
  private pricingData: PricingData | null = null;
  private lastFetched: Date | null = null;
  private readonly cacheExpiry = 1000 * 60 * 60 * 24; // 24 hour cache (as suggested)
  private readonly localStorageKey = 'openrouter_pricing_data';
  private readonly localStorageTimestampKey = 'openrouter_pricing_timestamp';

  /**
   * Fetch pricing data from OpenRouter API and normalize it
   */
  private async fetchPricingDataFromSource(): Promise<PricingData> {
    const response = await fetch(PRICING_DATA_URL);
    if (!response.ok) {
      throw new Error(`Failed to fetch pricing data: ${response.statusText}`);
    }
    
    const openRouterData: OpenRouterResponse = await response.json();
    
    // Normalize OpenRouter format to our internal format
    const normalizedData: PricingData = {};
    
    for (const model of openRouterData.data) {
      const p = model.pricing;
      if (!p) continue; // Skip models without pricing data
      
      const prompt = parseFloat(p.prompt as unknown as string);
      const completion = parseFloat(p.completion as unknown as string);
      const reasoning = p.internal_reasoning != null
        ? parseFloat(p.internal_reasoning as unknown as string)
        : undefined;
      
      // Skip models with invalid pricing data
      if (!Number.isFinite(prompt) || !Number.isFinite(completion)) continue;
      
      normalizedData[model.id] = {
        promptCost: prompt,
        completionCost: completion,
        reasoningCost: Number.isFinite(reasoning!) ? reasoning : undefined
      };
    }
    
    return normalizedData;
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

  /**
   * Normalize model name for fuzzy matching
   * Extracts the model identifier from various formats:
   * - models/gemini-2.5-flash -> gemini-2.5-flash
   * - google/gemini-2.5-flash -> gemini-2.5-flash
   * - gemini-2.5-flash -> gemini-2.5-flash
   */
  private normalizeModelName(modelName: string): string {
    // Remove common prefixes like "models/", "google/", "anthropic/", etc.
    return modelName.split('/').pop() || modelName;
  }

  /**
   * Get pricing information for a specific model with fuzzy matching
   * Tries multiple strategies to find the model:
   * 1. Exact match
   * 2. Normalized name match (after last slash)
   * 3. Search in all keys for normalized match
   */
  private getModelPricing(modelName: string) {
    if (!this.pricingData) {
      return null;
    }

    // Strategy 1: Try exact match first
    if (this.pricingData[modelName]) {
      return this.pricingData[modelName];
    }

    // Strategy 2: Normalize the input model name and try to find a match
    const normalizedInput = this.normalizeModelName(modelName);
    
    // Try to find a key in pricingData that ends with the normalized name
    for (const [key, value] of Object.entries(this.pricingData)) {
      const normalizedKey = this.normalizeModelName(key);
      
      // Check if normalized names match
      if (normalizedKey === normalizedInput) {
        console.log(`[PricingService] Model match found: "${modelName}" -> "${key}"`);
        return value;
      }
    }

    // No match found
    console.warn(`[PricingService] No pricing found for model: "${modelName}". Tried normalized: "${normalizedInput}"`);
    return null;
  }

  /**
   * Calculate cost based on token usage
   */
  calculateCost(modelName: string, tokenUsage: TokenUsage): CostCalculation | null {
    const modelPricing = this.getModelPricing(modelName);
    if (!modelPricing) {
      return null;
    }

    const inputCost = tokenUsage.inputTokens * modelPricing.promptCost;
    const outputCost = tokenUsage.outputTokens * modelPricing.completionCost;
    const reasoningCost = (tokenUsage.reasoningTokens || 0) * (modelPricing.reasoningCost || modelPricing.completionCost);
    const totalCost = inputCost + outputCost + reasoningCost;

    return {
      inputTokens: tokenUsage.inputTokens,
      outputTokens: tokenUsage.outputTokens,
      inputCost,
      outputCost: outputCost + reasoningCost,
      totalCost,
      modelName
    };
  }

  /**
   * Get pricing info for a model
   */
  getModelInfo(modelName: string) {
    return this.getModelPricing(modelName);
  }

  /**
   * Search models by query string
   */
  searchModels(query: string): Array<{ name: string; pricing: { promptCost: number; completionCost: number; reasoningCost?: number } }> {
    if (!this.pricingData) {
      return [];
    }

    const lowerQuery = query.toLowerCase();
    return Object.entries(this.pricingData)
      .filter(([name]) => name.toLowerCase().includes(lowerQuery))
      .map(([name, pricing]) => ({ name, pricing }));
  }

  /**
   * Get all available models
   */
  getAllModels(): Array<{ name: string; pricing: { promptCost: number; completionCost: number; reasoningCost?: number } }> {
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
