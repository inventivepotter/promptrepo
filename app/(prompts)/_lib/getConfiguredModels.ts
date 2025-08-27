import type { LLMProvider } from "@/types/LLMProvider";
import configuredModels from './configuredModels.json';
import { modelsApi } from './api/modelsApi';
import { errorNotification } from '@/lib/notifications';
export const getMockConfiguredModels = (): LLMProvider[] => {
  return configuredModels.providers;
};

export async function getConfiguredModels(): Promise<LLMProvider[]> {
  try {
    const providers = await modelsApi.getConfiguredModels();
    
    if (!providers || providers.length === 0) {
      
      errorNotification(
        'No Configured Providers',
        'The server returned no configured providers. Using local data.'
      );

      return configuredModels.providers;
    }

    
    return providers;
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    const errorName = error instanceof Error ? error.name : 'UnknownError';
    
    
    errorNotification(
      errorName || 'Connection Error',
      errorMessage || 'Unable to connect to provider service. Using local data.'
    );
    
    return configuredModels.providers;
  }
}
