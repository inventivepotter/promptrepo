import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

// Extract types from generated API schema
type BasicProvidersResponse = components['schemas']['BasicProvidersResponse'];
type ModelsResponse = components['schemas']['ModelsResponse'];
type FetchModelsRequest = components['schemas']['FetchModelsRequest'];

export const modelsApi = {
  // Get all available LLM providers (static list)
  getAvailableProviders: async (): Promise<OpenApiResponse<BasicProvidersResponse>> => {
    return await httpClient.get<BasicProvidersResponse>('/api/v0/llm/providers/available');
  },

  // Fetch models for a specific provider using API key
  fetchModelsByProvider: async (providerId: string, apiKey: string, apiBase: string = ''): Promise<OpenApiResponse<ModelsResponse>> => {
    const request: FetchModelsRequest = {
      provider: providerId,
      api_key: apiKey,
      api_base: apiBase
    };
    return await httpClient.post<ModelsResponse>(`/api/v0/llm/providers/models/${providerId}`, request);
  },
};

export default modelsApi;