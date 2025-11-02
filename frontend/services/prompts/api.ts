import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

// Type aliases for better readability
type PromptMeta = components['schemas']['PromptMeta'];
type PromptData = components['schemas']['PromptData'];
type PromptDataUpdate = components['schemas']['PromptDataUpdate'];
type DiscoverRepositoriesRequest = components['schemas']['DiscoverRepositoriesRequest'];

/**
 * Prompts API client matching backend endpoints
 * Uses the real backend API endpoints for prompt operations
 */
export const promptsApi = {
  /**
   * Get individual prompt by repository name and file path
   * GET /api/v0/prompts/{repo_name}/{file_path}
   */
  getPrompt: async (repoName: string, filePath: string): Promise<OpenApiResponse<PromptMeta>> => {
    const encodedRepoName = btoa(repoName);
    const encodedFilePath = btoa(filePath);
    
    return await httpClient.get<PromptMeta>(`/api/v0/prompts/${encodedRepoName}/${encodedFilePath}`);
  },

  /**
   * Save a prompt (create or update)
   * POST /api/v0/prompts/{repo_name}/{file_path}
   */
  savePrompt: async (
    repoName: string,
    filePath: string,
    promptData: PromptDataUpdate
  ): Promise<OpenApiResponse<PromptMeta>> => {
    const encodedRepoName = btoa(repoName);
    const encodedFilePath = filePath === 'new' ? 'new' : btoa(filePath);
    
    return await httpClient.post<PromptMeta>(
      `/api/v0/prompts/${encodedRepoName}/${encodedFilePath}`,
      promptData
    );
  },

  /**
   * Delete a prompt
   * DELETE /api/v0/prompts/{repo_name}/{file_path}
   */
  deletePrompt: async (repoName: string, filePath: string): Promise<OpenApiResponse<null>> => {
    const encodedRepoName = btoa(repoName);
    const encodedFilePath = btoa(filePath);
    
    return await httpClient.delete<null>(`/api/v0/prompts/${encodedRepoName}/${encodedFilePath}`);
  },

  /**
   * Discover prompts from one or more repositories
   * POST /api/v0/prompts/discover
   */
  discoverAllPromptsFromRepos: async (repoNames: string[]): Promise<OpenApiResponse<PromptMeta[]>> => {
    return await httpClient.post<PromptMeta[]>('/api/v0/prompts/discover', {
      repo_names: repoNames
    });
  },
};

// Re-export types for convenience
export type { PromptMeta, PromptData, PromptDataUpdate, DiscoverRepositoriesRequest };

export default promptsApi;