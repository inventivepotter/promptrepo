import { LLMProvider } from "../../../types/LLMProvider";
import { modelsApi } from './api/modelsApi';
import { errorNotification } from '@/lib/notifications';
import { getHostingType } from '@/utils/hostingType';

export async function getAvailableProviders(): Promise<{ providers: LLMProvider[] }> {
  try {
    // Check hosting type to determine whether to call backend
    const hostingType = await getHostingType();
    
    // For organization hosting type, return empty providers without backend call
    if (hostingType === 'organization') {
      return { providers: [] };
    }
    
    // For individual and other hosting types, call backend
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
