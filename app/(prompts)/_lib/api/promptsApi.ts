import httpClient from '@/lib/httpClient';
import type { Prompt } from '@/types/Prompt';
import type { ApiResult } from '@/types/ApiResponse';

export const promptsApi = {
  // Get all prompts
  getPrompts: async (): Promise<Prompt[]> => {
    const result = await httpClient.get<Prompt[]>('/v0/prompts');
    
    if (!result.success) {
      throw new Error(result.error || 'Failed to fetch prompts');
    }
    
    return result.data.map(p => ({
      ...p,
      created_at: new Date(p.created_at),
      updated_at: new Date(p.updated_at)
    }));
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