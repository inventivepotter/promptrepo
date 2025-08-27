import { Configuration } from "@/types/Configuration";
import { LLMProvider } from "@/types/LLMProvider";

export interface ConfigState {
  config: Configuration;
  currentStep: {
    step: number;
    selectedProvider: string;
    selectedModel: string;
    apiKey: string;
  };
  isLoading: boolean;
  availableModels: LLMProvider[];
}