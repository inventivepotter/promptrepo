import httpClient from '@/lib/httpClient';
import type { Configuration } from '@/types/Configuration';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';
/**
 * Configuration API client
 * All methods return OpenAPI-formatted responses
 */
type HostingConfig = components['schemas']['HostingConfig'];
type AppConfig = components['schemas']['AppConfig'];
export default class ConfigApi {
  /**
   * Get configuration
   * @returns OpenAPI response with configuration data
   */
  static async getConfig(): Promise<OpenApiResponse<AppConfig>> {
    return httpClient.get<AppConfig>('/api/v0/config');
  }

  /**
   * Update configuration
   * @param config - Partial configuration to update
   * @returns OpenAPI response with updated configuration
   */
  static async updateConfig(config: Partial<Configuration>): Promise<OpenApiResponse<Partial<AppConfig>>> {
    return httpClient.patch<Partial<AppConfig>>('/api/v0/config', config);
  }

  /**
   * Get hosting type without authentication
   * @returns OpenAPI response with hosting type
   */
  static async getHostingType(): Promise<OpenApiResponse<HostingConfig>> {
    return httpClient.get<HostingConfig>('/api/v0/config/hosting-type');
  }
}