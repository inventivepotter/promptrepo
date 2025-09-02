import httpClient from '@/lib/httpClient';
import type { ApiResult } from '@/types/ApiResponse';
import type { Repo } from '@/types/Repo';

export const reposApi = {
  // Update repository configuration
  updateRepos: async (repos: Repo[]): Promise<ApiResult<{ repos: Repo[] }>> => {
    return await httpClient.post<{ repos: Repo[] }>('/v0/repos/configured', { repos });
  },

};

export default reposApi;
