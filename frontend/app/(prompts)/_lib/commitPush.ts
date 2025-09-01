import { ApiResult } from '@/types/ApiResponse';
import { promptsApi } from './api/promptsApi';
import { successNotification, errorNotification } from '@/lib/notifications';

/**
 * Handle commit & push operations with proper notifications
 */
export const commitPushOperations = {
  /**
   * Commit and push a specific prompt
   */
  async commitPushPrompt(promptId: string): Promise<boolean> {
    try {
      const result = await promptsApi.commitPushPrompt(promptId);
      
      if (result.success) {
        successNotification(
          'Commit & Push Successful',
          'Your prompt has been committed and pushed to the repository'
        );
        return true;
      } else {
        errorNotification(
          'Commit & Push Failed',
          result.error || 'Failed to commit and push the prompt'
        );
        return false;
      }
    } catch (error) {
      console.error('Error during commit & push:', error);
      errorNotification(
        'Commit & Push Error',
        'An unexpected error occurred while committing and pushing'
      );
      return false;
    }
  },

  /**
   * Commit and push all prompts
   */
  async commitPushAll(): Promise<boolean> {
    try {
      const result = await promptsApi.commitPushAll();
      
      if (result.success) {
        successNotification(
          'Commit & Push Successful',
          'All prompts have been committed and pushed to the repository'
        );
        return true;
      } else {
        errorNotification(
          'Commit & Push Failed',
          result.error || 'Failed to commit and push all prompts'
        );
        return false;
      }
    } catch (error) {
      console.error('Error during commit & push all:', error);
      errorNotification(
        'Commit & Push Error',
        'An unexpected error occurred while committing and pushing all prompts'
      );
      return false;
    }
  }
};

export default commitPushOperations;