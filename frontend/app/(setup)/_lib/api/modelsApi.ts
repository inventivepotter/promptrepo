import httpClient from '@/lib/httpClient';
import type { LLMProvider } from '@/types/LLMProvider';
import type { ApiResult } from '@/types/ApiResponse';

export const modelsApi = {
  // Get all available LLM providers
  getAvailableModels: async (): Promise<ApiResult<LLMProvider[]>> => {
    return await httpClient.get<LLMProvider[]>('/v0/llm/providers/available');
  },
};

export default modelsApi;