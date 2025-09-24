import type { components } from '@/types/generated/api';

type AppConfigOutput = components['schemas']['AppConfig-Output'];
type BasicProviderInfo = components['schemas']['BasicProviderInfo'];
type RepoConfig = components['schemas']['RepoConfig'];
type RepoInfo = components['schemas']['RepoInfo'];
type LLMConfig = components['schemas']['LLMConfig'];

export interface ConfigState {
  config: AppConfigOutput;
  currentStep: {
    step: number;
    selectedProvider: string;
    selectedModel: string;
    apiKey: string;
    apiBaseUrl: string;
  };
  providers: {
    available: BasicProviderInfo[];
    configured: LLMConfig[];
    isLoading: boolean;
  };
  repos: {
    available: RepoInfo[];
    configured: RepoConfig[];
    isLoading: boolean;
  };
  isLoading: boolean;
  isSaving: boolean;
}