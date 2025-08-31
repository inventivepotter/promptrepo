import httpClient from '@/lib/httpClient';
import type { ApiResult } from '@/types/ApiResponse';

interface ProviderModels {
  id: string;
  name: string;
  models: Array<{ id: string; name: string }>;
}

interface ProviderModelsApiResponse {
  providers: ProviderModels[];
}

export const modelsApi = {
  // Get all configured LLM providers
  getConfiguredModels: async (): Promise<ApiResult<ProviderModelsApiResponse>> => {
    return await httpClient.get<ProviderModelsApiResponse>('/api/v0/llm/providers/configured');
  }
};

export default modelsApi;