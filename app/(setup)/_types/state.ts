import { Configuration } from "@/types/Configuration";

export interface ConfigState {
  config: Configuration;
  currentStep: {
    step: number;
    selectedProvider: string;
    selectedModel: string;
    apiKey: string;
  };
  isLoading: boolean;
}