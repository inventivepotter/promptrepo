import httpClient from '@/lib/httpClient';
import { getAuthHeaders } from '@/utils/authHeaders';
import type { Configuration } from '@/types/Configuration';
import type { ApiResult } from '@/types/ApiResponse';

export interface HostingTypeResponse {
  hosting_type: string;
}

export const configApi = {
  // Get configuration
  getConfig: async (): Promise<ApiResult<Configuration>> => {
    return await httpClient.get<Configuration>('/v0/config', {
      headers: getAuthHeaders()
    });
  },

  // Update configuration
  updateConfig: async (config: Partial<Configuration>): Promise<ApiResult<Configuration>> => {
    return await httpClient.patch<Configuration>('/v0/config', config, {
      headers: getAuthHeaders()
    });
  },

  // Get hosting type without authentication
  getHostingType: async (): Promise<ApiResult<HostingTypeResponse>> => {
    return await httpClient.get<HostingTypeResponse>('/v0/config/hosting-type');
  },

};

export default configApi;
