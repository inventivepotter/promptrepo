import httpClient from '@/lib/httpClient';
import type { LLMProvider, LLMProviderModel } from '@/types/LLMProvider';
import type { ApiResult } from '@/types/ApiResponse';

export const modelsApi = {
  // Get all available LLM providers (static list)
  getAvailableProviders: async (): Promise<ApiResult<{ providers: LLMProvider[] }>> => {
    return await httpClient.get<{ providers: LLMProvider[] }>('/v0/llm/providers/available');
  },

  // Fetch models for a specific provider using API key
  fetchModelsByProvider: async (provider: string, apiKey: string, apiBase: string = ''): Promise<ApiResult<{ models: LLMProviderModel[] }>> => {
    return await httpClient.post<{ models: LLMProviderModel[] }>(`/v0/llm/providers/models/${provider}`, {
      provider,
      api_key: apiKey,
      api_base: apiBase
    });
  },
};

export default modelsApi;