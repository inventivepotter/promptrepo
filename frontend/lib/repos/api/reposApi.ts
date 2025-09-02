import httpClient from '@/lib/httpClient';
import { getAuthHeaders } from '@/utils/authHeaders';
import type { Repo } from '@/types/Repo';
import type { ApiResponse } from '@/types/ApiResponse';

export const reposApi = {
  // Get all available repositories
  getAvailableRepos: async (): Promise<ApiResponse<Repo[]>> => {
    return await httpClient.get<Repo[]>('/api/v0/repos/available', {
      headers: getAuthHeaders()
    });
  },

  // Get configured repositories (for editor dropdown functionality)
  getConfiguredRepos: async (): Promise<ApiResponse<Repo[]>> => {
    return await httpClient.get<Repo[]>('/api/v0/repos/configured', {
      headers: getAuthHeaders()
    });
  },
};

export default reposApi;