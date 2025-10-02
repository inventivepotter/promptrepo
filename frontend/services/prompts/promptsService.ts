import { promptsApi } from './api';
import { errorNotification, successNotification } from '@/lib/notifications';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { PromptMeta, PromptDataUpdate } from './api';

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
    try {
      const result = await promptsApi.discoverAllPromptsFromRepos(repoNames);
      
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Discovery Failed',
          result.detail || `Failed to discover prompts from repository ${repoNames}`
        );
        return [];
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        return [];
      }

      const promptMetas = result.data;

      successNotification(
        'Repository Discovered',
        `Successfully discovered ${promptMetas.length} prompts from ${repoNames}`
      );
      
      return promptMetas;
    } catch (error: unknown) {
      console.error('Error discovering repository:', error);
      errorNotification(
        'Discovery Error',
        'An unexpected error occurred while discovering the repository'
      );
      return [];
    }
  }
}

// Export singleton instance
export const promptsService = new PromptsService();

// Export class for testing or custom instances
export default promptsService;