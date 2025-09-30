import { promptsApi } from './api';
import { errorNotification, successNotification } from '@/lib/notifications';
import { isStandardResponse, isErrorResponse, isPaginatedResponse } from '@/types/OpenApiResponse';
import type { Prompt, PromptCreate, PromptUpdate } from '@/types/Prompt';

/**
 * Prompts service that handles all prompt-related operations.
 * This includes CRUD operations, repository sync, and listing operations.
 * Following single responsibility principle - only handles prompt concerns.
 */
export class PromptsService {
  /**
   * Get all prompts with pagination and filtering
   * Handles error notifications
   */
  async getPrompts(params?: {
    query?: string;
    repo_name?: string;
    category?: string;
    tags?: string[];
    owner?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ prompts: Prompt[]; pagination?: { page: number; page_size: number; total_items: number; total_pages: number } }> {
    try {
      const result = await promptsApi.getPrompts(params);
      
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Prompts',
          result.detail || 'Unable to load prompts from server.'
        );
        
        // Handle authentication errors
        if (result.status_code === 401) {
          return { prompts: [] };
        }
        return { prompts: [] };
      }

      // Check if it's a paginated response
      if (isPaginatedResponse(result)) {
        return {
          prompts: result.data,
          pagination: result.pagination
        };
      }

      // Standard response with data array
      if (isStandardResponse(result) && Array.isArray(result.data)) {
        return { prompts: result.data };
      }

      return { prompts: [] };
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to prompt service.'
      );
      return { prompts: [] };
    }
  }

  /**
   * Get individual prompt by ID
   * Handles error notifications
   */
  async getPrompt(id: string): Promise<Prompt | null> {
    try {
      const result = await promptsApi.getPrompt(id);
      
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
  async createPrompt(promptData: PromptCreate): Promise<Prompt> {
    try {
      const result = await promptsApi.createPrompt(promptData);

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
  async updatePrompt(id: string, updates: PromptUpdate): Promise<Prompt> {
    try {
      const result = await promptsApi.updatePrompt(id, updates);

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
  async deletePrompt(id: string): Promise<void> {
    try {
      const result = await promptsApi.deletePrompt(id);

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
   * Sync prompts from a repository
   */
  async syncRepository(repoName: string): Promise<{ synced_count: number; repository: string } | null> {
    try {
      const result = await promptsApi.syncRepository(repoName);
      
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Sync Failed',
          result.detail || `Failed to sync repository ${repoName}`
        );
        return null;
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        return null;
      }

      successNotification(
        'Repository Synced',
        `Successfully synchronized ${result.data.synced_count} prompts from ${repoName}`
      );
      return result.data;
    } catch (error: unknown) {
      console.error('Error syncing repository:', error);
      errorNotification(
        'Sync Error',
        'An unexpected error occurred while syncing the repository'
      );
      return null;
    }
  }

  /**
   * List available repositories
   */
  async listRepositories(): Promise<Array<{
    name: string;
    path: string;
    type: string;
    has_git: boolean;
  }>> {
    try {
      const result = await promptsApi.listRepositories();
      
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to List Repositories',
          result.detail || 'Unable to load repositories from server.'
        );
        return [];
      }

      if (!isStandardResponse(result) || !result.data) {
        return [];
      }

      return result.data;
    } catch (error: unknown) {
      console.error('Error listing repositories:', error);
      errorNotification(
        'Connection Error',
        'Unable to connect to prompt service.'
      );
      return [];
    }
  }

  /**
   * List prompts in a specific repository
   */
  async listRepositoryPrompts(repoName: string): Promise<Prompt[]> {
    try {
      const result = await promptsApi.listRepositoryPrompts(repoName);
      
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to List Repository Prompts',
          result.detail || `Unable to load prompts from repository ${repoName}.`
        );
        return [];
      }

      if (!isStandardResponse(result) || !result.data) {
        return [];
      }

      return result.data;
    } catch (error: unknown) {
      console.error('Error listing repository prompts:', error);
      errorNotification(
        'Connection Error',
        'Unable to connect to prompt service.'
      );
      return [];
    }
  }

  /**
   * Discover prompt files in a repository
   */
  async discoverRepositoryPrompts(repoName: string): Promise<Array<{
    path: string;
    name: string;
    system_prompt: string | null;
    user_prompt: string | null;
    metadata: Record<string, unknown> | null;
  }>> {
    try {
      const result = await promptsApi.discoverRepositoryPrompts(repoName);
      
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Discover Prompts',
          result.detail || `Unable to discover prompts in repository ${repoName}.`
        );
        return [];
      }

      if (!isStandardResponse(result) || !result.data) {
        return [];
      }

      return result.data;
    } catch (error: unknown) {
      console.error('Error discovering repository prompts:', error);
      errorNotification(
        'Connection Error',
        'Unable to connect to prompt service.'
      );
      return [];
    }
  }

  /**
   * Legacy method for backward compatibility
   * @deprecated Use syncRepository instead
   */
  async commitPushPrompt(promptId: string): Promise<boolean> {
    // This is a placeholder since the backend doesn't have individual commit/push
    // You might want to call syncRepository with the prompt's repo_name instead
    errorNotification(
      'Operation Not Supported',
      'Individual prompt commit/push is not supported. Please sync the entire repository.'
    );
    return false;
  }

  /**
   * Legacy method for backward compatibility
   * @deprecated Use syncRepository instead
   */
  async commitPushAll(): Promise<boolean> {
    // This is a placeholder since the backend doesn't have this operation
    // You might want to sync all repositories instead
    errorNotification(
      'Operation Not Supported',
      'Bulk commit/push is not supported. Please sync individual repositories.'
    );
    return false;
  }
}

// Export singleton instance
export const promptsService = new PromptsService();

// Export class for testing or custom instances
export default promptsService;