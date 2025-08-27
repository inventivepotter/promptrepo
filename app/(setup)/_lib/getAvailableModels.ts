import { LLMProvider } from "../../../types/LLMProvider";
import availableModels from './availableModels.json';
import { modelsApi } from './api/modelsApi';
import { errorNotification } from '@/lib/notifications';

function getMockAvailableModels(): LLMProvider[] {
  return availableModels.providers;
}

export async function getAvailableModels(): Promise<LLMProvider[]> {
  try {
    const result = await modelsApi.getAvailableModels();

    if (!result.success) {

      errorNotification(
        result.error || 'No Available Providers',
        result.message || 'The server returned no available providers. Using local data.'
      );
      // return Promise.reject({error: result.error, message: result.message});

      return getMockAvailableModels();
    }

    return result.data;
  } catch (error: unknown) {
    
    errorNotification(
      'Connection Error',
      'Unable to connect to provider service. Using local data.'
    );
    // return Promise.reject(error);
    return getMockAvailableModels();
  }
}
