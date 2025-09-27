// Types for Config Store
import type { components } from '@/types/generated/api';

// Direct re-export of backend types
export type AppConfigOutput = components['schemas']['AppConfig-Output'];
export type AppConfigInput = components['schemas']['AppConfig-Input'];
export type HostingConfig = components['schemas']['HostingConfig'];
export type BasicProviderInfo = components['schemas']['BasicProviderInfo'];
export type RepoConfig = components['schemas']['RepoConfig'];
export type RepoInfo = components['schemas']['RepoInfo'];
export type LLMConfig = components['schemas']['LLMConfig'];
export type ModelInfo = components['schemas']['ModelInfo'];
export type BranchInfo = components['schemas']['BranchInfo'];

export interface ConfigState {
  config: AppConfigOutput;
  error: string | null;
  hostingType: string | null;
  availableLLMProviders: BasicProviderInfo[];
  availableRepos: RepoInfo[];
  
  // LLM form state
  llmProvider: string;
  apiKey: string;
  llmModel: string;
  apiBaseUrl: string;
  
  // Model loading state
  availableModels: ModelInfo[];
  isLoadingModels: boolean;

  // Branch loading state
  availableBranches: BranchInfo[];
  isLoadingBranches: boolean;
}

export interface ConfigActions {
  // Public actions
  getConfig: () => Promise<void>;
  updateConfig: (config: AppConfigInput) => Promise<void>;
  getHostingType: () => Promise<void>;
  
  // LLM Config actions
  addLLMConfig: (config: LLMConfig) => void;
  removeLLMConfig: (index: number) => void;
  loadAvailableLLMProviders: () => Promise<void>;
  getModels: () => Promise<ModelInfo[]>;
  setLLMProvider: (provider: string) => void;
  setApiKey: (apiKey: string) => void;
  setLLMModel: (model: string) => void;
  setApiBaseUrl: (url: string) => void;
  resetLLMForm: () => void;
  setAvailableModels: (models: ModelInfo[]) => void;
  setLoadingModels: (loading: boolean) => void;
  
  // Repo Config actions
  addRepoConfig: (config: RepoConfig) => void;
  removeRepoConfig: (index: number) => void;
  loadAvailableRepos: () => Promise<void>;
  updateConfiguredRepos: (repos: RepoConfig[]) => void;
  fetchBranches: (owner: string, repo: string) => Promise<void>;
  resetBranches: () => void;

  // Internal actions
  setError: (error: string | null) => void;
  setConfig: (config: AppConfigOutput) => void;
  setHostingType: (hostingType: string) => void;
  setAvailableProviders: (providers: BasicProviderInfo[]) => void;
  setAvailableRepos: (repos: RepoInfo[]) => void;
}

export type ConfigStore = ConfigState & ConfigActions;