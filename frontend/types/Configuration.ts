
export interface Configuration {
  hostingType: "individual" | "organization" | "multi-tenant" | "";
  githubClientId: string;
  githubClientSecret: string;
  llmConfigs: Array<LLMConfig>;
  adminEmails: string[];
}

export interface LLMConfig {
  provider: string;
  model: string;
  apiKey: string;
  apiBaseUrl?: string;
}

