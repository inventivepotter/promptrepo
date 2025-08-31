import { Configuration } from '@/types/Configuration'
import { configApi } from './api/configApi';
import { errorNotification } from '@/lib/notifications';
import { initConfig } from '../_state/configState';
import { ConfigError } from '../_types/state';

export interface GetConfigResult {
  config: Configuration;
  error: ConfigError | null;
}

export const getConfig = async (): Promise<GetConfigResult> => {
  try {
    const result = await configApi.getConfig();

    if (!result.success) {
      // Check if it's a 401 Unauthorized error
      if (result.statusCode === 401) {
        return {
          config: initConfig,
          error: {
            isUnauthorized: true,
            hasNoConfig: false,
            message: result.message || 'Unauthorized access. Please log in.'
          }
        };
      }
      
      // For other errors, show notification and return default config
      errorNotification(
        result.error || 'Configuration Load Failed',
        result.message || 'Unable to load configuration from server. Using local data.'
      );
      return {
        config: initConfig,
        error: {
          isUnauthorized: false,
          hasNoConfig: true,
          message: result.message || 'Failed to load configuration'
        }
      };
    }

    if (!result.data) {
      return {
        config: initConfig,
        error: {
          isUnauthorized: false,
          hasNoConfig: true,
          message: 'No configuration found on server'
        }
      };
    }

    return {
      config: result.data,
      error: null
    };
  } catch (error: unknown) {
    errorNotification(
      'Connection Error',
      'Unable to connect to configuration service. Using local data.'
    );
    return {
      config: initConfig,
      error: {
        isUnauthorized: false,
        hasNoConfig: true,
        message: 'Connection error'
      }
    };
  }
};