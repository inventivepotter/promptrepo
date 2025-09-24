import { useCallback } from 'react';
import { ConfigState } from '../_types/state';
import { ReposService } from '@/services/repos/reposService';
import { errorNotification } from '@/lib/notifications';
import type { components } from '@/types/generated/api';

type RepoConfig = components['schemas']['RepoConfig'];

export function useRepoConfigActions(
  configState: ConfigState,
  setConfigState: React.Dispatch<React.SetStateAction<ConfigState>>
) {
  // Load available repositories
  const loadRepos = useCallback(async () => {
    setConfigState(prev => ({
      ...prev,
      repos: { ...prev.repos, isLoading: true }
    }));

    try {
      const reposData = await ReposService.getAvailableRepos();
      // Keep RepoInfo format for ReposConfigStep component
      setConfigState(prev => ({
        ...prev,
        repos: {
          ...prev.repos,
          available: reposData.repositories,
          isLoading: false,
        }
      }));
    } catch (error) {
      console.error('Failed to load repositories:', error);
      setConfigState(prev => ({
        ...prev,
        repos: { ...prev.repos, isLoading: false }
      }));
    }
  }, [setConfigState]);

  // Add repo config
  const addRepoConfig = useCallback((repoName: string, branch: string) => {
    const repo = configState.repos.available.find(r => r.full_name === repoName);
    if (!repo) return;

    const newRepoConfig: RepoConfig = {
      id: "",
      repo_name: repo.full_name,
      repo_url: repo.clone_url,
      base_branch: branch,
      current_branch: branch,
    };

    // Check for duplicates
    const isDuplicate = configState.config.repo_configs?.some(existing =>
      existing.repo_name === newRepoConfig.repo_name &&
      existing.base_branch === newRepoConfig.base_branch
    );

    if (isDuplicate) {
      errorNotification(
        'Duplicate Repository',
        'This repository configuration already exists.'
      );
      return;
    }

    setConfigState(prev => ({
      ...prev,
      config: {
        ...prev.config,
        repo_configs: [...(prev.config.repo_configs || []), newRepoConfig],
      }
    }));
  }, [configState.repos.available, configState.config.repo_configs, setConfigState]);

  // Remove repo config
  const removeRepoConfig = useCallback((index: number) => {
    setConfigState(prev => ({
      ...prev,
      config: {
        ...prev.config,
        repo_configs: prev.config.repo_configs?.filter((_, i) => i !== index) || []
      }
    }));
  }, [setConfigState]);

  // Update repos
  const updateConfiguredRepos = useCallback((repos: RepoConfig[]) => {
    setConfigState(prev => ({
      ...prev,
      repos: { ...prev.repos, configured: repos }
    }));
  }, [setConfigState]);

  return {
    loadRepos,
    addRepoConfig,
    removeRepoConfig,
    updateConfiguredRepos,
  };
}