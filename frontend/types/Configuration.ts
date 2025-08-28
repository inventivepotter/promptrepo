
export interface Configuration {
  hostingType: "self" | "multi-user" | "";
  githubClientId: string;
  githubClientSecret: string;
  llmConfigs: Array<LLMConfig>;
}

export interface LLMConfig {
  provider: string;
  model: string;
  apiKey: string;
}

