import { toolsApi } from './api';
import { errorNotification } from '@/lib/notifications';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { ToolDefinition, ToolSummary } from '@/types/tools';

export class ToolsService {
  /**
   * List all tools from a repository
   * @param repoName - The repository name
   * @returns Array of tool summaries
   */
  static async listTools(repoName: string = 'default'): Promise<ToolSummary[]> {
    try {
      const result = await toolsApi.listTools(repoName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Tools',
          result.detail || 'Unable to load tools from the repository.'
        );
        throw new Error(result.detail || 'Failed to load tools');
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
        'Unable to connect to tools service.'
      );
      throw error;
    }
  }

  /**
   * Get a specific tool by name
   * @param toolName - The tool name
   * @param repoName - The repository name
   * @returns The tool definition
   */
  static async getTool(toolName: string, repoName: string = 'default'): Promise<ToolDefinition> {
    try {
      const result = await toolsApi.getTool(toolName, repoName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Load Tool',
          result.detail || `Unable to load tool "${toolName}".`
        );
        throw new Error(result.detail || 'Failed to load tool');
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
        `Unable to load tool "${toolName}".`
      );
      throw error;
    }
  }

  /**
   * Create or update a tool
   * @param tool - The tool definition
   * @param repoName - The repository name
   * @returns The saved tool definition with PR info
   */
  static async saveTool(tool: ToolDefinition, repoName: string = 'default'): Promise<{ tool: ToolDefinition; pr_info?: { pr_url?: string; pr_number?: number; pr_id?: number } | null }> {
    try {
      const result = await toolsApi.saveTool(tool, repoName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Save Tool',
          result.detail || 'Unable to save the tool.'
        );
        throw new Error(result.detail || 'Failed to save tool');
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
        'Unable to save tool.'
      );
      throw error;
    }
  }

  /**
   * Delete a tool
   * @param toolName - The tool name
   * @param repoName - The repository name
   */
  static async deleteTool(toolName: string, repoName: string = 'default'): Promise<void> {
    try {
      const result = await toolsApi.deleteTool(toolName, repoName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Delete Tool',
          result.detail || `Unable to delete tool "${toolName}".`
        );
        throw new Error(result.detail || 'Failed to delete tool');
      }

      if (!isStandardResponse(result)) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }
    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        `Unable to delete tool "${toolName}".`
      );
      throw error;
    }
  }

  /**
   * Validate a tool
   * @param toolName - The tool name
   * @param repoName - The repository name
   * @returns Validation result
   */
  static async validateTool(toolName: string, repoName: string = 'default'): Promise<{ valid: boolean; errors?: string[] }> {
    try {
      const result = await toolsApi.validateTool(toolName, repoName);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Failed to Validate Tool',
          result.detail || `Unable to validate tool "${toolName}".`
        );
        throw new Error(result.detail || 'Failed to validate tool');
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
        `Unable to validate tool "${toolName}".`
      );
      throw error;
    }
  }
}