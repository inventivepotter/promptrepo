import httpClient from '@/lib/httpClient';
import type { Repo } from '@/types/Repo';
import type { ApiResult, ApiResponse } from '@/types/ApiResponse';

export const reposApi = {
  // Get all available repositories
  getAvailableRepos: async (): Promise<ApiResponse<Repo[]>> => {
    return await httpClient.get<Repo[]>('/v0/repos/available');
  },

  // Get configured repositories
  getConfiguredRepos: async (userId?: string): Promise<ApiResponse<Repo[]>> => {
    const endpoint = userId ? `/v0/repos/configured?userId=${userId}` : '/v0/repos/configured';
    return await httpClient.get<Repo[]>(endpoint);
  },

  // Configure a new repository
  configureRepo: async (repo: Omit<Repo, 'id'>): Promise<ApiResult<Repo>> => {
    return await httpClient.post<Repo>(
      '/v0/repos/configure',
      repo
    );
  },

  // Update repository configuration
  updateRepoConfig: async (id: string, updates: Partial<Repo>): Promise<ApiResult<Repo>> => {
    return await httpClient.patch<Repo>(
      `/v0/repos/${id}/config`,
      updates
    );
  },

  // Remove repository from configured list
  removeRepo: async (repoId: string): Promise<ApiResult<void>> => {
    return await httpClient.delete<void>(`/v0/repos/${repoId}`);
  },
};

export default reposApi;