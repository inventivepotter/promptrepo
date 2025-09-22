import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

// Extract types from generated API schema
type AppConfigInput = components['schemas']['AppConfig-Input'];
type AppConfigOutput = components['schemas']['AppConfig-Output'];
type RepoConfig = components['schemas']['RepoConfig'];

export const reposApi = {
  // Update repository configuration via the main config API
  updateRepos: async (repos: RepoConfig[]): Promise<OpenApiResponse<AppConfigOutput>> => {
    const configUpdate: Partial<AppConfigInput> = {
      repo_configs: repos
    };
    return await httpClient.patch<AppConfigOutput>('/api/v0/config/', configUpdate);
  },
};

export default reposApi;
