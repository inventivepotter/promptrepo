import { PromptJson } from '../_types/PromptState';
import { Prompt } from '@/types/Prompt';
import prompts from './prompts.json';
import { promptsApi } from './api/promptsApi';
import { errorNotification } from '@/lib/notifications';

function getMockPrompts(): Prompt[] {
  return (prompts as PromptJson[]).map((p) => ({
    ...p,
    created_at: new Date(p.created_at),
    updated_at: new Date(p.updated_at),
  }));
}

export async function getPrompts(): Promise<Prompt[]> {
  try {
    const result = await promptsApi.getPrompts();
    
    if (!result.success) {
      
      // Show user-friendly notification
      errorNotification(
        result.error || 'Prompt Sync Failed',
        result.message || 'Unable to load prompts from server. Using local data.'
      );
      
      return getMockPrompts();
    }

    if (!result.data || result.data.length === 0) {
      
      errorNotification(
        'No Prompts Found',
        'The server returned no prompts. Using local data.'
      );

      return getMockPrompts();
    }

  
    const data = result.data.map(p => ({
      ...p,
      created_at: new Date(p.created_at),
      updated_at: new Date(p.updated_at)
    }));
    return data;
  } catch (error: unknown) {
    // Enhanced error handling with proper type checking
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    const errorName = error instanceof Error ? error.name : 'UnknownError';
    
    
    // Show user-friendly notification
    errorNotification(
      errorName || 'Connection Error',
      errorMessage || 'Unable to connect to prompt service. Using local data.'
    );

    return getMockPrompts();
  }
}
