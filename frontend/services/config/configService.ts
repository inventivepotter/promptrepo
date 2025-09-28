import ConfigApi from './api';
import { errorNotification } from '@/lib/notifications';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

type AppConfigInput = components['schemas']['AppConfig-Input'];
type AppConfigOutput = components['schemas']['AppConfig-Output'];

export class ConfigService {
  /**
   * Get configuration
   * @returns The application configuration
   */
  static async getConfig(): Promise<AppConfigOutput> {
    try {
      const result = await ConfigApi.getConfig();

      // Handle error responses - show toast and throw error
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Configuration Load Failed',
          result.detail || 'Unable to load configuration from server.'
        );
        throw new Error(result.detail || 'Configuration load failed');
      }

      if (!isStandardResponse(result) || !result.data) {
         errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      return result.data;

    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to configuration service.'
      );
      throw error;
    }
  }

  /**
   * Update configuration
   * @param config - The configuration to update
   * @returns The updated configuration
   */
  static async updateConfig(config: AppConfigInput): Promise<AppConfigOutput> {
    try {
      const result = await ConfigApi.updateConfig(config);

      // Handle error responses - show toast and throw error
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Configuration Save Failed',
          result.detail || 'Unable to save configuration on server. Changes may not be saved.'
        );
        throw new Error(result.detail || 'Configuration save failed');
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Configuration Save Failed',
          'Unexpected response format from server.'
        );
        throw new Error('Unexpected response format');
      }

      return result.data;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to configuration service. Changes may not be saved.'
      );
      throw error;
    }
  }

  static isIndividualHosting(hostingType?: string): boolean {
    return !hostingType || hostingType === 'individual';
  }


  static shouldSkipAuth(hostingType?: string): boolean {
    return ConfigService.isIndividualHosting(hostingType);
  }
}