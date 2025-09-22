import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

// Extract types from generated API schema
type ProvidersResponse = components['schemas']['ProvidersResponse'];

export const modelsApi = {
  // Get all configured LLM providers
  getConfiguredModels: async (): Promise<OpenApiResponse<ProvidersResponse>> => {
    return await httpClient.get<ProvidersResponse>('/api/v0/llm/providers/configured');
  }
};

export default modelsApi;