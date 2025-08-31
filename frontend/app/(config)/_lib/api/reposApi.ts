import httpClient from '@/lib/httpClient';
import { getAuthHeaders } from '@/utils/authHeaders';
import type { ApiResult } from '@/types/ApiResponse';
import type { Repo } from '@/types/Repo';

export const reposApi = {
  // Update repository configuration
  updateRepos: async (repos: Repo[]): Promise<ApiResult<{ repos: Repo[] }>> => {
    return await httpClient.post<{ repos: Repo[] }>('/v0/repos/configured', { repos }, {
      headers: getAuthHeaders()
    });
  },

};

export default reposApi;
