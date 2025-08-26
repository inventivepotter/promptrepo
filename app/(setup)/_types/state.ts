export interface SetupData {
  hostingType: "self" | "multi-user" | "";
  githubClientId: string;
  githubClientSecret: string;
  llmConfigs: Array<{
    provider: string;
    model: string;
    apiKey: string;
  }>;
  currentStep: {
    step: number;
    selectedProvider: string;
    selectedModel: string;
    apiKey: string;
  };
}