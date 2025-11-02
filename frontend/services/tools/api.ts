import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

// Type aliases from generated types
type ToolMeta = components['schemas']['ToolMeta'];
type ToolData = components['schemas']['ToolData-Input'];

/**
 * Tools API client matching backend endpoints
 * Uses the real backend API endpoints for tool operations
 */
export const toolsApi = {
  /**
   * List all tools in a repository
   * GET /api/v0/tools/?repo_name=...
   */
  listTools: async (repoName: string = 'default'): Promise<OpenApiResponse<ToolMeta[]>> => {
    const searchParams = new URLSearchParams();
    searchParams.append('repo_name', repoName);
    
    return await httpClient.get<ToolMeta[]>(`/api/v0/tools/?${searchParams.toString()}`);
  },

  /**
   * Get a specific tool by file path
   * GET /api/v0/tools/{repo_name}/{file_path}
   */
  getTool: async (repoName: string, filePath: string): Promise<OpenApiResponse<ToolMeta>> => {
    const encodedRepoName = btoa(repoName);
    const encodedFilePath = btoa(filePath);
    
    return await httpClient.get<ToolMeta>(`/api/v0/tools/${encodedRepoName}/${encodedFilePath}`);
  },

  /**
   * Create or update a tool
   * POST /api/v0/tools/{repo_name}/{file_path}
   */
  saveTool: async (repoName: string, filePath: string, toolData: ToolData): Promise<OpenApiResponse<ToolMeta>> => {
    const encodedRepoName = btoa(repoName);
    const encodedFilePath = filePath === 'new' ? 'new' : btoa(filePath);
    
    return await httpClient.post<ToolMeta>(
      `/api/v0/tools/${encodedRepoName}/${encodedFilePath}`,
      toolData
    );
  },

  /**
   * Delete a tool
   * DELETE /api/v0/tools/{repo_name}/{file_path}
   */
  deleteTool: async (repoName: string, filePath: string): Promise<OpenApiResponse<{ deleted: boolean; file_path: string }>> => {
    const encodedRepoName = btoa(repoName);
    const encodedFilePath = btoa(filePath);
    
    return await httpClient.delete<{ deleted: boolean; file_path: string }>(`/api/v0/tools/${encodedRepoName}/${encodedFilePath}`);
  },

  /**
   * Validate a tool
   * POST /api/v0/tools/{repo_name}/{file_path}/validate
   */
  validateTool: async (repoName: string, filePath: string): Promise<OpenApiResponse<{ valid: boolean; file_path: string }>> => {
    const encodedRepoName = btoa(repoName);
    const encodedFilePath = btoa(filePath);
    
    return await httpClient.post<{ valid: boolean; file_path: string }>(
      `/api/v0/tools/${encodedRepoName}/${encodedFilePath}/validate`
    );
  },
};

export default toolsApi;