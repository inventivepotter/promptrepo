import { promptsApi } from './api';
import { errorNotification, successNotification } from '@/lib/notifications';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { PromptMeta, PromptDataUpdate } from './api';
import { usePromptStore } from '@/stores/promptStore/store';
import { useConfigStore } from '@/stores/configStore/configStore';

/**
 * Prompts service that handles all prompt-related operations.
 * Works directly with PromptMeta from the backend API.
 * Following single responsibility principle - only handles prompt concerns.
 */
export class PromptsService {
  /**
   * Get individual prompt by repository name and file path
   * Handles error notifications
   */
  async getPrompt(repoName: string, filePath: string): Promise<PromptMeta | null> {
    try {
      const result = await promptsApi.getPrompt(repoName, filePath);
      
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Prompt',
          result.detail || 'Unable to load prompt from server.'
        );
        
        // Handle authentication errors
        if (result.status_code === 401) {
          return null;
        }
        return null;
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Prompt Not Found',
          'The requested prompt could not be found.'
        );
        return null;
      }

      return result.data;
    } catch (error: unknown) {
      console.error('Error fetching prompt:', error);
      errorNotification(
        'Connection Error',
        'Unable to connect to prompt service.'
      );
      return null;
    }
  }

  /**
   * Create a new prompt
   */
  async createPrompt(promptMeta: PromptMeta): Promise<PromptMeta> {
    try {
      const result = await promptsApi.createPrompt(
        promptMeta.repo_name,
        promptMeta.file_path,
        promptMeta.prompt
      );

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Prompt Creation Failed',
          result.detail || 'Unable to create prompt on server.'
        );
        throw new Error(result.detail || 'Prompt creation failed');
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      successNotification(
        'Prompt Created',
        'Your prompt has been created successfully.'
      );

      return result.data;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to prompt service.'
      );
      throw error;
    }
  }

  /**
   * Update a prompt
   * Handles error notifications and validation
   */
  async updatePrompt(repoName: string, filePath: string, updates: PromptDataUpdate): Promise<PromptMeta> {
    try {
      const result = await promptsApi.updatePrompt(repoName, filePath, updates);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Prompt Update Failed',
          result.detail || 'Unable to update prompt on server.'
        );
        throw new Error(result.detail || 'Prompt update failed');
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      successNotification(
        'Prompt Updated',
        'Your prompt has been updated successfully.'
      );

      return result.data;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to prompt service.'
      );
      throw error;
    }
  }

  /**
   * Delete a prompt
   */
  async deletePrompt(repoName: string, filePath: string): Promise<void> {
    try {
      const result = await promptsApi.deletePrompt(repoName, filePath);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Prompt Deletion Failed',
          result.detail || 'Unable to delete prompt on server.'
        );
        throw new Error(result.detail || 'Prompt deletion failed');
      }

      successNotification(
        'Prompt Deleted',
        'Your prompt has been deleted successfully.'
      );
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to prompt service.'
      );
      throw error;
    }
  }

  /**
   * Discover prompts from a repository
   */
  async discoverAllPromptsFromRepos(repoNames: string[]): Promise<PromptMeta[]> {
    // Return empty array immediately if no repos provided
    if (!repoNames || repoNames.length === 0) {
      console.log('No repositories to discover prompts from');
      return [];
    }
    
    try {
      const result = await promptsApi.discoverAllPromptsFromRepos(repoNames);
      
      if (isErrorResponse(result)) {
        // Log error but don't show notification - let the store handle it
        console.error('Discovery failed:', result.detail || result.title);
        
        // Handle authentication errors - throw to prevent retries
        if (result.status_code === 401) {
          console.warn('Authentication required (401) - User needs to log in');
          throw new Error('AUTHENTICATION_REQUIRED');
        }
        
        // If 400 Bad Request, invalidate both caches to force refresh
        if (result.status_code === 400) {
          console.warn('Bad Request (400) - Invalidating prompt and config caches');
          
          // Invalidate prompt cache
          usePromptStore.getState().invalidateCache();
          
          // Invalidate config cache
          useConfigStore.getState().invalidateCache();
        }
        
        return [];
      }

      if (!isStandardResponse(result) || !result.data) {
        console.error('Unexpected response format from discovery API');
        return [];
      }

      const promptMetas = result.data;

      // // Only show success notification if prompts were actually discovered
      // if (promptMetas.length > 0) {
      //   successNotification(
      //     'Repository Discovered',
      //     `Successfully discovered ${promptMetas.length} prompts from ${repoNames.length} repository/repositories`
      //   );
      // }
      
      return promptMetas;
    } catch (error: unknown) {
      console.error('Error discovering repository:', error);
      // Re-throw authentication errors to prevent retries
      if (error instanceof Error && error.message === 'AUTHENTICATION_REQUIRED') {
        throw error;
      }
      // Log but don't show notification to avoid spam
      return [];
    }
  }
}

// Export singleton instance
export const promptsService = new PromptsService();

// Export class for testing or custom instances
export default promptsService;