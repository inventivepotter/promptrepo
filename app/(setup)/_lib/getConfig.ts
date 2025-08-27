import { Configuration } from '@/types/Configuration'
import mockConfigData from './config.json';
import { configApi } from './api/configApi';
import { errorNotification } from '@/lib/notifications';

function fetchMockConfigData(): Configuration {
  return mockConfigData as Configuration;
};

export const getConfig = async (): Promise<Configuration> => {
  try {
    const result = await configApi.getConfig();

    if (!result.success) {

      errorNotification(
        result.error || 'Configuration Load Failed',
        result.message || 'Unable to load configuration from server. Using local data.'
      );
      // return Promise.reject({error: result.error, message: result.message});
      return fetchMockConfigData();
    }

    if (!result.data) {
      
      errorNotification(
        'No Configuration Found',
        'The server returned no configuration. Using local data.'
      );

      return fetchMockConfigData();
    }

    return result.data;
  } catch (error: unknown) {
    
    errorNotification(
      'Connection Error',
      'Unable to connect to configuration service. Using local data.'
    );
    // return Promise.reject(error);
    return fetchMockConfigData();
  }
};