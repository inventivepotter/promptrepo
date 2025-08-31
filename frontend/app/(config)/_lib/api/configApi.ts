import httpClient from '@/lib/httpClient';
import { getAuthHeaders } from '@/utils/authHeaders';
import type { Configuration } from '@/types/Configuration';
import type { ApiResult } from '@/types/ApiResponse';

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

  // Export configuration
  exportConfig: async (): Promise<ApiResult<{ config: Configuration; timestamp: string }>> => {
    return await httpClient.get<{ config: Configuration; timestamp: string }>('/v0/config/export', {
      headers: getAuthHeaders()
    });
  },

};

export default configApi;