export interface ModelPricing {
  input_cost_per_token: number;
  output_cost_per_token: number;
  output_cost_per_reasoning_token?: number;
  litellm_provider: string;
}

export interface PricingData {
  [modelName: string]: ModelPricing;
}

export interface CostCalculation {
  inputTokens: number;
  outputTokens: number;
  inputCost: number;
  outputCost: number;
  totalCost: number;
  modelName: string;
  provider: string;
}

export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  reasoningTokens?: number;
}