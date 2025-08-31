import type { LLMProvider } from "@/types/LLMProvider";
import { modelsApi } from './api/modelsApi';
import { errorNotification } from '@/lib/notifications';

export async function getConfiguredModels(): Promise<LLMProvider[]> {
  try {
    const result = await modelsApi.getConfiguredModels();

    if (!result.success) {

      errorNotification(
        result.error || 'No Configured Providers',
        result.message || 'The server returned no configured providers. Using local data.'
      );

      return [];
    }

    // Transform the API response to flatten individual models for the dropdown
    const flattenedModels: LLMProvider[] = [];
    result.data?.providers?.forEach(provider => {
      provider.models.forEach(model => {
        flattenedModels.push({
          id: `${provider.id}/${model.id}`,
          name: `${provider.id}/${model.id}`,
          custom_api_base: false // Default value since this isn't used in model selection
        });
      });
    });

    return flattenedModels;
  } catch (error: unknown) {
    // return Promise.reject(error);
    errorNotification(
      'Connection Error',
      'Unable to connect to provider service. Using local data.'
    );

    return [];
  }
}
