import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

/**
 * Models API client
 * All methods return OpenAPI-formatted responses
 */
type BasicProvidersResponse = components['schemas']['BasicProvidersResponse'];
type ModelsResponse = components['schemas']['ModelsResponse'];
type FetchModelsRequest = components['schemas']['FetchModelsRequest'];
type ProvidersResponse = components['schemas']['ProvidersResponse'];
export default class ModelsApi {
  /**
   * Get all available LLM providers (static list)
   * @returns OpenAPI response with available providers
   */
  static async getAvailableProviders(): Promise<OpenApiResponse<BasicProvidersResponse>> {
    return await httpClient.get<BasicProvidersResponse>('/api/v0/llm/providers/available');
  }

  /**
   * Fetch models for a specific provider using API key
   * @param providerId - The provider ID
   * @param apiKey - The API key for the provider
   * @param apiBase - Optional API base URL
   * @returns OpenAPI response with models data
   */
  static async fetchModelsByProvider(providerId: string, apiKey: string, apiBase: string = ''): Promise<OpenApiResponse<ModelsResponse>> {
    const request: FetchModelsRequest = {
      api_key: apiKey,
      api_base: apiBase
    };
    return await httpClient.post<ModelsResponse>(`/api/v0/llm/provider/${providerId}/models`, request);
  }

  /**
   * Get all configured LLM providers
   * @returns OpenAPI response with configured providers
   */
  static async getConfiguredModels(): Promise<OpenApiResponse<ProvidersResponse>> {
    return await httpClient.get<ProvidersResponse>('/api/v0/llm/providers/configured');
  }
}