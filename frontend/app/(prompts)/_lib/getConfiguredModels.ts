import type { LLMProvider } from "@/types/LLMProvider";
import configuredModels from './configuredModels.json';
import { modelsApi } from './api/modelsApi';
import { errorNotification } from '@/lib/notifications';
export const getMockConfiguredModels = (): LLMProvider[] => {
  return configuredModels.providers;
};

export async function getConfiguredModels(): Promise<LLMProvider[]> {
  try {
    const result = await modelsApi.getConfiguredModels();

    if (!result.success) {

      errorNotification(
        result.error || 'No Configured Providers',
        result.message || 'The server returned no configured providers. Using local data.'
      );
      // return Promise.reject({error: result.error, message: result.message});

      return configuredModels.providers;
    }

    return result.data;
  } catch (error: unknown) {
    // return Promise.reject(error);
    errorNotification(
      'Connection Error',
      'Unable to connect to provider service. Using local data.'
    );
    
    return configuredModels.providers;
  }
}
