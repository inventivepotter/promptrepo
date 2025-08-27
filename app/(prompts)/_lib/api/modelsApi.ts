import httpClient from '@/lib/httpClient';
import type { LLMProvider } from '@/types/LLMProvider';
import type { ApiResult } from '@/types/ApiResponse';

export const modelsApi = {
  // Get all configured LLM providers
  getConfiguredModels: async (): Promise<ApiResult<LLMProvider[]>> => {
    return await httpClient.get<LLMProvider[]>('/v0/llm/providers/configured');
  },

  // Add a new LLM provider
  addModel: async (provider: Omit<LLMProvider, 'id'>): Promise<ApiResult<LLMProvider>> => {
    return await httpClient.post<LLMProvider>('/v0/llm/providers/configured', provider);
  },

  // Update an existing LLM provider
  updateModel: async (id: string, updates: Partial<LLMProvider>): Promise<ApiResult<LLMProvider>> => {
    return await httpClient.patch<LLMProvider>(`/v0/llm/providers/configured/${id}`, updates);
  },

  // Remove a LLM provider
  removeModel: async (id: string): Promise<ApiResult<void>> => {
    return await httpClient.delete<void>(`/v0/llm/providers/configured/${id}`);
  },
};

export default modelsApi;