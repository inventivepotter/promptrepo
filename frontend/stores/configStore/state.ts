// Initial state for Config Store
import type { ConfigState } from './types';

export const initialConfigState: ConfigState = {
  config: {
    hosting_config: null,
    oauth_configs: null,
    llm_configs: null,
    repo_configs: null,
  },
  error: null,
  availableLLMProviders: [],
  availableRepos: [],
  
  // Config loading state - starts as true to show skeleton on initial load
  isLoadingConfig: true,
  
  // LLM form state
  llmProvider: '',
  apiKey: '',
  llmModel: '',
  apiBaseUrl: '',
  
  // Model loading state
  availableModels: [],
  isLoadingModels: false,

  // Branch loading state
  availableBranches: [],
  isLoadingBranches: false,

  // Repo form state
  selectedRepo: '',
  selectedBranch: '',
  isSaving: false,
  repoSearchValue: '',
  branchSearchValue: '',

  // LLM form UI state
  providerSearchValue: '',
  modelSearchValue: '',
};