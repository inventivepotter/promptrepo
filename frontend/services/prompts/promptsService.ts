import { promptsApi } from './api';
import { errorNotification, successNotification } from '@/lib/notifications';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { Prompt, CommitInfo } from '@/types/Prompt';
import type { PromptJson } from '@/app/(prompts)/_types/PromptState';

// Mock data imports - these should be moved to a separate mock service when backend is fully implemented
import prompts from './prompts.json';
import promptCommits from './promptCommits.json';

/**
 * Prompts service that handles all prompt-related operations.
 * This includes CRUD operations, commit/push operations, and template utilities.
 * Following single responsibility principle - only handles prompt concerns.
 */
export class PromptsService {
  /**
   * Mock data helpers - consolidate all mock operations
   * @private
   */
  private getMockData() {
    const commitHistory = promptCommits as CommitInfo[];
    const mockPrompts = (prompts as PromptJson[]).map((p) => ({
      ...p,
      created_at: new Date(p.created_at),
      updated_at: new Date(p.updated_at),
      recent_commits: commitHistory
    }));

    return {
      prompts: mockPrompts,
      findById: (id: string) => mockPrompts.find(p => p.id === id) || null
    };
  }

  /**
   * Get all prompts
   * Handles error notifications and fallback to mock data
   */
  async getPrompts(): Promise<Prompt[]> {
    try {
      const result = await promptsApi.getPrompts();
      
      if (isErrorResponse(result)) {
        // Show user-friendly notification
        errorNotification(
          result.title || 'Prompt Sync Failed',
          result.detail || 'Unable to load prompts from server. Using local data.'
        );
        
        // Handle authentication errors differently
        if (result.status_code === 401) {
          return [];
        }
        return this.getMockData().prompts;
      }

      if (!isStandardResponse(result) || !result.data || result.data.length === 0) {
        errorNotification(
          'No Prompts Found',
          'The server returned no prompts. Using local data.'
        );
        return this.getMockData().prompts;
      }

      const data = result.data.map(p => ({
        ...p,
        created_at: new Date(p.created_at),
        updated_at: new Date(p.updated_at)
      }));
      return data;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to prompt service. Using local data.'
      );
      return this.getMockData().prompts;
    }
  }

  /**
   * Get individual prompt with commit history
   * Handles error notifications and fallback to mock data
   */
  async getPrompt(id: string): Promise<Prompt | null> {
    try {
      const result = await promptsApi.getPrompt(id);
      
      if (isErrorResponse(result)) {
        // Show user-friendly notification and fall back to mock data
        errorNotification(
          result.title || 'Failed to Load Prompt',
          result.detail || 'Unable to load prompt from server. Using local data.'
        );
        // Handle authentication errors differently
        if (result.status_code === 401) {
          return null;
        }
        return this.getMockData().findById(id);
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Prompt Not Found',
          'The requested prompt could not be found on server. Using local data.'
        );
        return this.getMockData().findById(id);
      }

      // Convert date strings to Date objects
      const data = {
        ...result.data,
        created_at: new Date(result.data.created_at),
        updated_at: new Date(result.data.updated_at)
      };
      
      return data;
    } catch (error: unknown) {
      console.error('Error fetching prompt:', error);
      errorNotification(
        'Connection Error',
        'Unable to connect to prompt service. Using local data.'
      );
      return this.getMockData().findById(id);
    }
  }

  /**
   * Update a prompt
   * Handles error notifications and validation
   */
  async updatePrompt(updates: Partial<Prompt>): Promise<Prompt> {
    try {
      // Ensure id is always included for updates
      if (!updates.id) {
        errorNotification(
          'Prompt Update Failed',
          'Prompt ID is required for updates.'
        );
        throw new Error('Prompt ID is required for updates.');
      }

      // Add artificial delay for better UX feedback
      await new Promise((resolve) => setTimeout(resolve, 1000));

      const result = await promptsApi.updatePrompt(updates);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Prompt Update Failed',
          result.detail || 'Unable to update prompt on server. Changes may not be saved.'
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

      return result.data;
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to prompt service. Changes may not be saved.'
      );
      throw error;
    }
  }

  /**
   * Create a new prompt
   */
  async createPrompt(prompt: Omit<Prompt, 'id' | 'created_at' | 'updated_at'>): Promise<Prompt> {
    try {
      const result = await promptsApi.createPrompt(prompt);

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
   * Commit and push a specific prompt
   */
  async commitPushPrompt(promptId: string): Promise<boolean> {
    try {
      const result = await promptsApi.commitPushPrompt(promptId);
      
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Commit & Push Failed',
          result.detail || 'Failed to commit and push the prompt'
        );
        return false;
      }

      if (!isStandardResponse(result)) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        return false;
      }

      successNotification(
        'Commit & Push Successful',
        'Your prompt has been committed and pushed to the repository'
      );
      return true;
    } catch (error: unknown) {
      console.error('Error during commit & push:', error);
      errorNotification(
        'Commit & Push Error',
        'An unexpected error occurred while committing and pushing'
      );
      return false;
    }
  }

  /**
   * Commit and push all prompts
   */
  async commitPushAll(): Promise<boolean> {
    try {
      const result = await promptsApi.commitPushAll();
      
      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Commit & Push Failed',
          result.detail || 'Failed to commit and push all prompts'
        );
        return false;
      }

      if (!isStandardResponse(result)) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        return false;
      }

      successNotification(
        'Commit & Push Successful',
        'All prompts have been committed and pushed to the repository'
      );
      return true;
    } catch (error: unknown) {
      console.error('Error during commit & push all:', error);
      errorNotification(
        'Commit & Push Error',
        'An unexpected error occurred while committing and pushing all prompts'
      );
      return false;
    }
  }
}

// Export singleton instance
export const promptsService = new PromptsService();

// Export class for testing or custom instances
export default promptsService;