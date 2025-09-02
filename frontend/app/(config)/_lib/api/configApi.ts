import httpClient from '@/lib/httpClient';
import type { Configuration } from '@/types/Configuration';
import type { ApiResult } from '@/types/ApiResponse';

export interface HostingTypeResponse {
  hosting_type: string;
}

export const configApi = {
  // Get configuration
  getConfig: async (): Promise<ApiResult<Configuration>> => {
    return await httpClient.get<Configuration>('/api/v0/config');
  },

  // Update configuration
  updateConfig: async (config: Partial<Configuration>): Promise<ApiResult<Configuration>> => {
    return await httpClient.patch<Configuration>('/api/v0/config', config);
  },

  // Get hosting type without authentication
  getHostingType: async (): Promise<ApiResult<HostingTypeResponse>> => {
    return await httpClient.get<HostingTypeResponse>('/api/v0/config/hosting-type');
  },

};

export default configApi;
