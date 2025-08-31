import { Configuration } from "@/types/Configuration";
import { LLMProvider } from "@/types/LLMProvider";

export interface ConfigError {
  isUnauthorized: boolean;
  hasNoConfig: boolean;
  message?: string;
}

export interface ConfigState {
  config: Configuration;
  currentStep: {
    step: number;
    selectedProvider: string;
    selectedModel: string;
    apiKey: string;
    apiBaseUrl: string;
  };
  providers: {
    available: LLMProvider[];
    isLoading: boolean;
    error: string | null;
  };
  isLoading: boolean;
  isSaving: boolean;
  error: ConfigError | null;
}