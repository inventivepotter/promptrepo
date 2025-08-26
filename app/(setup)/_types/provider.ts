export interface Provider {
  id: string;
  name: string;
  models: Array<{ id: string; name: string }>;
}

export interface LLMConfig {
  provider: string;
  model: string;
  apiKey: string;
}