import httpClient from '@/lib/httpClient';
import type { OpenApiResponse, PaginatedResponse } from '@/types/OpenApiResponse';
import type { Prompt, PromptCreate, PromptUpdate } from '@/types/Prompt';

/**
 * Prompts API client matching backend endpoints
 * Uses the real backend API endpoints for prompt operations
 */
export const promptsApi = {
  /**
   * Get all prompts with pagination and filtering
   * GET /api/v0/prompts
   */
  getPrompts: async (params?: {
    query?: string;
    repo_name?: string;
    category?: string;
    tags?: string[];
    owner?: string;
    page?: number;
    page_size?: number;
  }): Promise<OpenApiResponse<Prompt[]>> => {
    const searchParams = new URLSearchParams();
    
    if (params?.query) searchParams.append('query', params.query);
    if (params?.repo_name) searchParams.append('repo_name', params.repo_name);
    if (params?.category) searchParams.append('category', params.category);
    if (params?.tags) {
      params.tags.forEach(tag => searchParams.append('tags', tag));
    }
    if (params?.owner) searchParams.append('owner', params.owner);
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.page_size) searchParams.append('page_size', params.page_size.toString());

    const queryString = searchParams.toString();
    const url = queryString ? `/api/v0/prompts?${queryString}` : '/api/v0/prompts';
    
    return await httpClient.get<Prompt[]>(url);
  },

  /**
   * Get individual prompt by ID
   * GET /api/v0/prompts/{id}
   */
  getPrompt: async (id: string): Promise<OpenApiResponse<Prompt>> => {
    return await httpClient.get<Prompt>(`/api/v0/prompts/${id}`);
  },

  /**
   * Create a new prompt
   * POST /api/v0/prompts
   */
  createPrompt: async (prompt: PromptCreate): Promise<OpenApiResponse<Prompt>> => {
    return await httpClient.post<Prompt>(
      '/api/v0/prompts',
      prompt
    );
  },

  /**
   * Update a prompt
   * PUT /api/v0/prompts/{id}
   */
  updatePrompt: async (id: string, updates: PromptUpdate): Promise<OpenApiResponse<Prompt>> => {
    return await httpClient.put<Prompt>(
      `/api/v0/prompts/${id}`,
      updates
    );
  },

  /**
   * Delete a prompt
   * DELETE /api/v0/prompts/{id}
   */
  deletePrompt: async (id: string): Promise<OpenApiResponse<void>> => {
    return await httpClient.delete<void>(`/api/v0/prompts/${id}`);
  },

  /**
   * Sync prompts from a repository
   * POST /api/v0/prompts/sync/{repo_name}
   */
  syncRepository: async (repoName: string): Promise<OpenApiResponse<{ synced_count: number; repository: string }>> => {
    return await httpClient.post<{ synced_count: number; repository: string }>(
      `/api/v0/prompts/sync/${repoName}`,
      {}
    );
  },

  /**
   * List available repositories
   * GET /api/v0/prompts/repositories/list
   */
  listRepositories: async (): Promise<OpenApiResponse<Array<{
    name: string;
    path: string;
    type: string;
    has_git: boolean;
  }>>> => {
    return await httpClient.get<Array<{
      name: string;
      path: string;
      type: string;
      has_git: boolean;
    }>>('/api/v0/prompts/repositories/list');
  },

  /**
   * List prompts in a specific repository
   * GET /api/v0/prompts/repositories/{repo_name}/prompts
   */
  listRepositoryPrompts: async (repoName: string): Promise<OpenApiResponse<Prompt[]>> => {
    return await httpClient.get<Prompt[]>(`/api/v0/prompts/repositories/${repoName}/prompts`);
  },

  /**
   * Discover prompt files in a repository
   * GET /api/v0/prompts/repositories/{repo_name}/discover
   */
  discoverRepositoryPrompts: async (repoName: string): Promise<OpenApiResponse<Array<{
    path: string;
    name: string;
    system_prompt: string | null;
    user_prompt: string | null;
    metadata: Record<string, unknown> | null;
  }>>> => {
    return await httpClient.get<Array<{
      path: string;
      name: string;
      system_prompt: string | null;
      user_prompt: string | null;
      metadata: Record<string, unknown> | null;
    }>>(`/api/v0/prompts/repositories/${repoName}/discover`);
  }
};

export default promptsApi;