import type { Prompt } from '@/types/Prompt';
import promptsApi from './api/promptsApi';
import { errorNotification } from '@/lib/notifications';

export async function updatePrompt(updates: Partial<Prompt>) {
  try {
    // Ensure id is always included for updates
    if (!updates.id) {
      errorNotification(
        'Prompt Update Failed',
        'Prompt ID is required for updates.'
      );
      return Promise.reject({error: 'Prompt Update Failed', message: 'Prompt ID is required for updates.'});
    }

    await new Promise((resolve) => setTimeout(resolve, 1000));

    const result = await promptsApi.updatePrompt(updates);

    if (!result.success) {
      errorNotification(
        result.error || 'Prompt Update Failed',
        result.message || 'Unable to update prompt on server. Changes may not be saved.'
      );
      console.log("1");
      return Promise.reject({error: result.error, message: result.message});
    }

    return result;
  } catch (error: unknown) {
    console.log("2")
    errorNotification(
      'Connection Error',
      'Unable to connect to prompt service. Changes may not be saved.'
    );
    return Promise.reject(error);
  }
}