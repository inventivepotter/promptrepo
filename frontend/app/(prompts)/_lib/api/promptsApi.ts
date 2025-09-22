import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { Prompt } from '@/types/Prompt';

// Note: Prompt endpoints may not be implemented in backend yet
// These are placeholders that follow the OpenAPI pattern

export const promptsApi = {
  // Get all prompts
  getPrompts: async (): Promise<OpenApiResponse<Prompt[]>> => {
    return await httpClient.get<Prompt[]>('/api/v0/prompts');
  },

  // Get individual prompt with commit history
  getPrompt: async (id: string): Promise<OpenApiResponse<Prompt>> => {
    return await httpClient.get<Prompt>(`/api/v0/prompts/${id}`);
  },

  // Update a prompt
  updatePrompt: async (updates: Partial<Prompt>): Promise<OpenApiResponse<Prompt>> => {
    if (!updates.id) {
      throw new Error('Prompt ID is required for updates');
    }

    return await httpClient.patch<Prompt>(
      `/api/v0/prompts/${updates.id}`,
      updates
    );
  },

  // Create a new prompt
  createPrompt: async (prompt: Omit<Prompt, 'id' | 'created_at' | 'updated_at'>): Promise<OpenApiResponse<Prompt>> => {
    return await httpClient.post<Prompt>(
      '/api/v0/prompts',
      prompt
    );
  },

  // Delete a prompt
  deletePrompt: async (id: string): Promise<OpenApiResponse<void>> => {
    return await httpClient.delete<void>(`/api/v0/prompts/${id}`);
  },

  // Commit and push specific prompt
  commitPushPrompt: async (promptId: string): Promise<OpenApiResponse<void>> => {
    return await httpClient.post<void>('/api/v0/prompts/commit-push', {
      prompt_id: promptId
    });
  },

  // Commit and push all prompts
  commitPushAll: async (): Promise<OpenApiResponse<void>> => {
    return await httpClient.post<void>('/api/v0/prompts/commit-push', {
      all: true
    });
  }
};

export default promptsApi;