import httpClient from '@/lib/httpClient';
import type { LLMProvider } from '@/types/LLMProvider';
import type { ApiResult } from '@/types/ApiResponse';

export interface ModelOption {
  value: string;  // format: "providerId/modelId"
  label: string;  // format: "Model Name (Provider Name)"
}

export const llmProvidersApi = {
  // Get all configured LLM providers
  getConfiguredProviders: async (): Promise<LLMProvider[]> => {
    const result = await httpClient.get<LLMProvider[]>('/v0/llm/providers');
    
    if (!result.success) {
      throw new Error(result.error || 'Failed to fetch LLM providers');
    }
    
    return result.data;
  },

  // Get all available models as formatted options
  getModelOptions: async (): Promise<ModelOption[]> => {
    const providers = await llmProvidersApi.getConfiguredProviders();
    
    return providers.flatMap(provider =>
      provider.models.map(model => ({
        value: `${provider.id}/${model.id}`,
        label: `${model.name} (${provider.name})`
      }))
    );
  },

  // Add a new LLM provider
  addProvider: async (provider: Omit<LLMProvider, 'id'>): Promise<ApiResult<LLMProvider>> => {
    return await httpClient.post<LLMProvider>('/v0/llm/providers', provider);
  },

  // Update an existing LLM provider
  updateProvider: async (id: string, updates: Partial<LLMProvider>): Promise<ApiResult<LLMProvider>> => {
    return await httpClient.patch<LLMProvider>(`/v0/llm/providers/${id}`, updates);
  },

  // Remove a LLM provider
  removeProvider: async (id: string): Promise<ApiResult<void>> => {
    return await httpClient.delete<void>(`/v0/llm/providers/${id}`);
  },

  // Test provider configuration
  testProvider: async (id: string): Promise<ApiResult<{ isValid: boolean; message?: string }>> => {
    return await httpClient.post<{ isValid: boolean; message?: string }>(
      `/v0/llm/providers/${id}/test`
    );
  }
};

export default llmProvidersApi;