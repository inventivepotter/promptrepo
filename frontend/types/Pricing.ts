// OpenRouter API format
export interface OpenRouterPricing {
  prompt: string;        // Cost per token for input (as string)
  completion: string;    // Cost per token for output (as string)
  request: string;       // Cost per request
  image: string;         // Cost per image
  web_search?: string;   // Cost per web search
  internal_reasoning?: string; // Cost for internal reasoning tokens
}

export interface OpenRouterModel {
  id: string;
  canonical_slug?: string;
  name: string;
  pricing?: OpenRouterPricing;
  context_length?: number;
}

export interface OpenRouterResponse {
  data: OpenRouterModel[];
}

// Normalized pricing data (model ID -> pricing info)
export interface PricingData {
  [modelId: string]: {
    promptCost: number;        // Cost per token for input
    completionCost: number;    // Cost per token for output
    reasoningCost?: number;    // Cost per reasoning token
  };
}

export interface CostCalculation {
  inputTokens: number;
  outputTokens: number;
  inputCost: number;
  outputCost: number;
  totalCost: number;
  modelName: string;
}

export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  reasoningTokens?: number;
}