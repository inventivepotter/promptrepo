import httpClient from '@/lib/httpClient';
import { getAuthHeaders } from '@/utils/authHeaders';
import type { Prompt } from '@/types/Prompt';
import type { ApiResult, ApiResponse } from '@/types/ApiResponse';

export const promptsApi = {
  // Get all prompts
  getPrompts: async (): Promise<ApiResponse<Prompt[]>> => {
    return await httpClient.get<Prompt[]>('/api/v0/prompts', {
      headers: getAuthHeaders()
    });
  },

  // Get individual prompt with commit history
  getPrompt: async (id: string): Promise<ApiResponse<Prompt>> => {
    return await httpClient.get<Prompt>(`/api/v0/prompts/${id}`, {
      headers: getAuthHeaders()
    });
  },

  // Update a prompt
  updatePrompt: async (updates: Partial<Prompt>): Promise<ApiResult<Prompt>> => {
    if (!updates.id) {
      throw new Error('Prompt ID is required for updates');
    }

    return await httpClient.patch<Prompt>(
      `/api/v0/prompts/${updates.id}`,
      updates,
      {
        headers: getAuthHeaders()
      }
    );
  },

  // Create a new prompt
  createPrompt: async (prompt: Omit<Prompt, 'id' | 'created_at' | 'updated_at'>): Promise<ApiResult<Prompt>> => {
    return await httpClient.post<Prompt>(
      '/api/v0/prompts',
      prompt,
      {
        headers: getAuthHeaders()
      }
    );
  },

  // Delete a prompt
  deletePrompt: async (id: string): Promise<ApiResult<void>> => {
    return await httpClient.delete<void>(`/api/v0/prompts/${id}`, {
      headers: getAuthHeaders()
    });
  },

  // Commit and push specific prompt
  commitPushPrompt: async (promptId: string): Promise<ApiResult<void>> => {
    return await httpClient.post<void>('/api/v0/prompts/commit-push', {
      prompt_id: promptId
    }, {
      headers: getAuthHeaders()
    });
  },

  // Commit and push all prompts
  commitPushAll: async (): Promise<ApiResult<void>> => {
    return await httpClient.post<void>('/api/v0/prompts/commit-push', {
      all: true
    }, {
      headers: getAuthHeaders()
    });
  }
};

export default promptsApi;