import ConfigApi from './api';
import { errorNotification } from '@/lib/notifications';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';
import { globalCache } from '@/lib/cache';

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

      // Handle error responses - show toast and return original config
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Configuration Save Failed',
          result.detail || 'Unable to save configuration on server. Changes may not be saved.'
        );
        return config as AppConfigOutput;
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Configuration Save Failed',
          'Unexpected response format from server.'
        );
        return config as AppConfigOutput;
      }

      return result.data;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to configuration service. Changes may not be saved.'
      );
      return config as AppConfigOutput;
    }
  }

  /**
   * Get the resolved hosting type string with caching and fallback logic.
   * @returns Promise<string> - The hosting type (e.g., 'individual', 'organization')
   */
  static async getHostingType(): Promise<string> {
    const cacheKey = 'hosting-type';
    
    // Return cached value if it exists
    const cachedValue = globalCache.get<string>(cacheKey);
    if (cachedValue) {
      return cachedValue;
    }

    // Return existing promise if one is already in flight
    const existingPromise = globalCache.getPromise<string>(cacheKey);
    if (existingPromise) {
      return existingPromise;
    }

    // Create new promise
    const promise = ConfigService.fetchAndResolveHostingType();
    globalCache.setPromise(cacheKey, promise);

    try {
      const type = await promise;
      globalCache.set(cacheKey, type);
      return type;
    } catch (error) {
      // Return cached value if available, otherwise default to individual
      return cachedValue || 'individual';
    }
  }

  private static async fetchAndResolveHostingType(): Promise<string> {
    try {
      const result = await ConfigApi.getHostingType();

      // Handle error responses
      if (isErrorResponse(result)) {
        console.warn('Failed to fetch hosting type:', result.detail || result.title);
        return 'individual';
      }

      
      if (!isStandardResponse(result) || !result.data) {
        console.warn('Failed to fetch hosting type, defaulting to individual:');
        return 'individual';
      }

      return result.data.type || 'individual';
    } catch (error) {
      console.warn('Failed to fetch hosting type, defaulting to individual:', error);
      return 'individual';
    }
  }

  static isIndividualHosting(hostingType?: string): boolean {
    return !hostingType || hostingType === 'individual';
  }


  static shouldSkipAuth(hostingType?: string): boolean {
    return ConfigService.isIndividualHosting(hostingType);
  }

  static clearHostingTypeCache(): void {
    globalCache.clear('hosting-type');
  }
}