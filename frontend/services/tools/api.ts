import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { ToolDefinition, ToolSummary, ValidateToolResponse } from '@/types/tools';

/**
 * Tools API client matching backend endpoints
 * Uses the real backend API endpoints for tool operations
 */
export const toolsApi = {
  /**
   * List all tools in a repository
   * GET /api/v0/tools/?repo_name=...
   */
  listTools: async (repoName: string): Promise<OpenApiResponse<ToolSummary[]>> => {
    const searchParams = new URLSearchParams();
    searchParams.append('repo_name', repoName);
    
    return await httpClient.get<ToolSummary[]>(`/api/v0/tools/?${searchParams.toString()}`);
  },

  /**
   * Get a specific tool by name
   * GET /api/v0/tools/{tool_name}?repo_name=...
   */
  getTool: async (toolName: string, repoName: string): Promise<OpenApiResponse<ToolDefinition>> => {
    const searchParams = new URLSearchParams();
    searchParams.append('repo_name', repoName);
    
    return await httpClient.get<ToolDefinition>(`/api/v0/tools/${encodeURIComponent(toolName)}?${searchParams.toString()}`);
  },

  /**
   * Create or update a tool
   * POST /api/v0/tools/
   */
  saveTool: async (tool: ToolDefinition, repoName: string): Promise<OpenApiResponse<{ tool: ToolDefinition; pr_info?: { pr_url?: string; pr_number?: number; pr_id?: number } | null }>> => {
    return await httpClient.post<{ tool: ToolDefinition; pr_info?: { pr_url?: string; pr_number?: number; pr_id?: number } | null }>(
      '/api/v0/tools/',
      {
        repo_name: repoName,
        ...tool
      }
    );
  },

  /**
   * Delete a tool
   * DELETE /api/v0/tools/{tool_name}?repo_name=...
   */
  deleteTool: async (toolName: string, repoName: string): Promise<OpenApiResponse<null>> => {
    const searchParams = new URLSearchParams();
    searchParams.append('repo_name', repoName);
    
    return await httpClient.delete<null>(`/api/v0/tools/${encodeURIComponent(toolName)}?${searchParams.toString()}`);
  },

  /**
   * Validate a tool
   * POST /api/v0/tools/{tool_name}/validate?repo_name=...
   */
  validateTool: async (toolName: string, repoName: string): Promise<OpenApiResponse<ValidateToolResponse>> => {
    const searchParams = new URLSearchParams();
    searchParams.append('repo_name', repoName);
    
    return await httpClient.post<ValidateToolResponse>(
      `/api/v0/tools/${encodeURIComponent(toolName)}/validate?${searchParams.toString()}`
    );
  },
};

export default toolsApi;