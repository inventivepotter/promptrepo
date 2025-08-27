import { Configuration } from '@/types/Configuration';
import { configApi } from './api/configApi';
import { errorNotification } from '@/lib/notifications';
import { initConfig } from '../_state/configState';

export const postConfig = async (config: Configuration): Promise<Configuration> => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));

    const result = await configApi.updateConfig(config);

    if (!result.success) {
      
      errorNotification(
        result.error || 'Configuration Save Failed',
        result.message || 'Unable to save configuration on server. Changes may not be saved.'
      );

      return initConfig;
    }

    return result.data;
  } catch (error: unknown) {
  
    errorNotification(
      'Connection Error',
      'Unable to connect to configuration service. Changes may not be saved.'
    );
    return initConfig;
  }
};
