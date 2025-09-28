// Combined config store actions
import { createGetConfigAction } from './getConfig';
import { createUpdateConfigAction } from './updateConfig';
import { createAddLLMConfigAction } from './addLLMConfig';
import { createRemoveLLMConfigAction } from './removeLLMConfig';
import { createLoadProvidersAction } from './loadAvailableLLMProviders';
import { createAddRepoConfigAction } from './addRepoConfig';
import { createRemoveRepoConfigAction } from './removeRepoConfig';
import { createLoadReposAction } from './loadAvailableRepos';
import { createUpdateConfiguredReposAction } from './updateConfiguredRepos';
import { createSetErrorAction } from './setError';
import { createSetConfigAction } from './setConfig';
import { createSetAvailableProvidersAction } from './setAvailableProviders';
import { createSetAvailableReposAction } from './setAvailableRepos';
import { createGetModelsAction } from './getModels';
import { createLLMActions } from './llmActions';
import { createGetRepoBranchesAction } from './getRepoBranches';
import { createRepoFormActions } from './repoFormActions';
import { createLLMFormActions } from './llmFormActions';
import { createSetLLMProviderWithSideEffectsAction } from './setLLMProviderWithSideEffects';
import { createFetchModelsIfReadyAction } from './fetchModelsIfReady';
import { createInitializeConfigAction } from './initializeConfig';
import { createLogoutAction } from './logout';
import type { StateCreator } from '@/lib/zustand';
import type { ConfigStore, ConfigActions } from '../types';

// Combine all actions into a single StateCreator
export const createConfigActions: StateCreator<ConfigStore, [], [], ConfigActions> = (set, get, api) => ({
  // Public actions
  ...createGetConfigAction(set, get, api),
  ...createUpdateConfigAction(set, get, api),
  ...createInitializeConfigAction(set, get, api),
  ...createLogoutAction(set, get, api),
  ...createLoadProvidersAction(set, get, api),
  ...createLoadReposAction(set, get, api),

  // LLM Config actions
  ...createAddLLMConfigAction(set, get, api),
  ...createRemoveLLMConfigAction(set, get, api),
  ...createGetModelsAction(set, get, api),
  ...createLLMActions(set, get, api),

  // LLM side effect actions
  ...createSetLLMProviderWithSideEffectsAction(set, get, api),
  ...createFetchModelsIfReadyAction(set, get, api),

  // Repo Config actions
  ...createAddRepoConfigAction(set, get, api),
  ...createRemoveRepoConfigAction(set, get, api),
  ...createUpdateConfiguredReposAction(set, get, api),
  ...createGetRepoBranchesAction(set, get, api),
  
  // Repo form actions
  ...createRepoFormActions(set, get, api),

  // LLM form actions
  ...createLLMFormActions(set, get, api),

  // Internal actions
  ...createSetErrorAction(set, get, api),
  ...createSetConfigAction(set, get, api),
  ...createSetAvailableProvidersAction(set, get, api),
  ...createSetAvailableReposAction(set, get, api),
});