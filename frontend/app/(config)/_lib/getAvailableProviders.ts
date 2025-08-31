import { LLMProvider, LLMProviderModel } from "../../../types/LLMProvider";
import { modelsApi } from './api/modelsApi';
import { errorNotification } from '@/lib/notifications';

export async function getAvailableProviders(): Promise<{ providers: LLMProvider[] }> {
  try {
    const result = await modelsApi.getAvailableProviders();

    if (!result.success) {

      errorNotification(
        result.error || 'No Available Providers',
        result.message || 'The server returned no available providers. Using local data.'
      );
      return { providers: [] };
    }

    return result.data;
  } catch (error: unknown) {
    
    errorNotification(
      'Connection Error',
      'Unable to connect to provider service. Using local data.'
    );
    return { providers: [] };
  }
}
