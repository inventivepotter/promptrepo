import { useCallback } from 'react';
import { PromptsState } from '../_types/PromptState';

export type PromptStateUpdater = (
  updater: PromptsState | ((prev: PromptsState) => PromptsState),
  shouldPersist?: boolean
) => void;

export interface GitHubLoginFunctions {
  handleGitHubLogin: () => Promise<void>;
}

export function useHandleGithubLogin(
  updateCurrentRepoStepField: (field: keyof PromptsState['currentRepoStep'], value: string | boolean) => void
): GitHubLoginFunctions {
  const handleGitHubLogin = useCallback(async () => {
    setTimeout(() => {
      updateCurrentRepoStepField('isLoggedIn', true);
    }, 1000);
  }, [updateCurrentRepoStepField]);

  return {
    handleGitHubLogin,
  };
}