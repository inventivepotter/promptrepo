import httpClient from '@/lib/httpClient';
import type { Prompt } from '@/types/Prompt';
import type { ApiResult, ApiResponse } from '@/types/ApiResponse';

export const promptsApi = {
  // Get all prompts
  getPrompts: async (): Promise<ApiResponse<Prompt[]>> => {
    return await httpClient.get<Prompt[]>('/v0/prompts');
  },

  // Update a prompt
  updatePrompt: async (updates: Partial<Prompt>): Promise<ApiResult<Prompt>> => {
    if (!updates.id) {
      throw new Error('Prompt ID is required for updates');
    }

    return await httpClient.patch<Prompt>(
      `/v0/prompts/${updates.id}`,
      updates
    );
  },

  // Create a new prompt
  createPrompt: async (prompt: Omit<Prompt, 'id' | 'created_at' | 'updated_at'>): Promise<ApiResult<Prompt>> => {
    return await httpClient.post<Prompt>(
      '/v0/prompts',
      prompt
    );
  },

  // Delete a prompt
  deletePrompt: async (id: string): Promise<ApiResult<void>> => {
    return await httpClient.delete<void>(`/v0/prompts/${id}`);
  }
};

export default promptsApi;