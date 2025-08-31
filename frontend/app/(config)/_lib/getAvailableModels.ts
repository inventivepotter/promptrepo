import { LLMProviderModel } from "@/types/LLMProvider";
import { errorNotification } from "@/lib/notifications";
import modelsApi from "./api/modelsApi";

export async function getAvailableModels(provider_id: string, api_key: string, api_base: string = ''): Promise<{ models: LLMProviderModel[] }> {
  try {
    const result = await modelsApi.fetchModelsByProvider(provider_id, api_key, api_base);

    if (!result.success) {
      errorNotification(
        result.error || 'Unable to fetch models',
        result.message || 'There was an error fetching models.'
      );
      return { models: [] };
    }

    if (Array.isArray(result.data.models) && result.data.models.length === 0) {
      errorNotification(
        'No Available Models',
        'The server returned no available models for this provider.'
      );
      return { models: [] };
    }

    return result.data;
  } catch (error: unknown) {
    errorNotification(
      'Connection Error',
      'Unable to connect to provider service to fetch models.'
    );
    return { models: [] };
  }
}
