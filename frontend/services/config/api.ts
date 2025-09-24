import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

/**
 * Configuration API client
 * All methods return OpenAPI-formatted responses
 */
type HostingConfig = components['schemas']['HostingConfig'];
type AppConfigInput = components['schemas']['AppConfig-Input'];
type AppConfigOutput = components['schemas']['AppConfig-Output'];

export default class ConfigApi {
  /**
   * Get configuration
   * @returns OpenAPI response with configuration data
   */
  static async getConfig(): Promise<OpenApiResponse<AppConfigOutput>> {
    return httpClient.get<AppConfigOutput>('/api/v0/config');
  }

  /**
   * Update configuration
   * @param config - Configuration to update
   * @returns OpenAPI response with updated configuration
   */
  static async updateConfig(config: AppConfigInput): Promise<OpenApiResponse<AppConfigOutput>> {
    return httpClient.patch<AppConfigOutput>('/api/v0/config', config);
  }

  /**
   * Get hosting type without authentication
   * @returns OpenAPI response with hosting type
   */
  static async getHostingType(): Promise<OpenApiResponse<HostingConfig>> {
    return httpClient.get<HostingConfig>('/api/v0/config/hosting-type');
  }
}