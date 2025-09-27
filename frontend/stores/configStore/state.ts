// Initial state for Config Store
import type { ConfigState } from './types';

export const initialConfigState: ConfigState = {
  config: {
    hosting_config: {
      type: 'individual',
    },
    llm_configs: [],
    repo_configs: [],
  },
  error: null,
  hostingType: null,
  availableProviders: [],
  availableRepos: [],
  
  // LLM form state
  llmProvider: '',
  apiKey: '',
  llmModel: '',
  apiBaseUrl: '',
  
  // Model loading state
  availableModels: [],
  isLoadingModels: false,
};