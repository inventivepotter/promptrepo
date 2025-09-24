import { errorNotification } from "@/lib/notifications";
import ModelsApi from "./api";
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';
import type { LLMProvider } from '@/types/LLMProvider';

type ModelsResponse = components['schemas']['ModelsResponse'];
type BasicProvidersResponse = components['schemas']['BasicProvidersResponse'];
type ProvidersResponse = components['schemas']['ProvidersResponse'];

export class LLMProviderService {
  static async getAvailableProviders(): Promise<BasicProvidersResponse> {
    try {
      const result = await ModelsApi.getAvailableProviders();

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'No Available Providers',
          result.detail || 'The server returned no available providers.'
        );
        throw new Error(result.detail || 'Failed to load providers');
      }

      if (isStandardResponse(result) && result.data) {
        return result.data;
      }

      throw new Error('Unexpected response format');
    } catch (error: unknown) {
      errorNotification('Connection Error', 'Unable to connect to provider service.');
      throw error;
    }
  }

  static async getAvailableModels(provider_id: string, api_key: string, api_base: string = ''): Promise<ModelsResponse> {
    try {
      const result = await ModelsApi.fetchModelsByProvider(provider_id, api_key, api_base);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Unable to fetch models',
          result.detail || 'There was an error fetching models.'
        );
        throw new Error(result.detail || 'Failed to fetch models');
      }

      if (isStandardResponse(result) && result.data) {
        if (Array.isArray(result.data.models) && result.data.models.length === 0) {
          errorNotification('No Available Models', 'The server returned no available models for this provider.');
        }
        return result.data;
      }

      throw new Error('Unexpected response format');
    } catch (error: unknown) {
      errorNotification('Connection Error', 'Unable to connect to provider service to fetch models.');
      throw error;
    }
  }

  static async getConfiguredModels(): Promise<ProvidersResponse> {
    try {
      const result = await ModelsApi.getConfiguredModels();

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'No Configured Providers',
          result.detail || 'The server returned no configured providers.'
        );
        throw new Error(result.detail || 'Failed to load configured providers');
      }

      if (isStandardResponse(result) && result.data) {
        return result.data;
      }

      throw new Error('Unexpected response format');
    } catch (error: unknown) {
      errorNotification('Connection Error', 'Unable to connect to provider service.');
      throw error;
    }
  }

  static async getConfiguredModelsFlattened(): Promise<LLMProvider[]> {
    try {
      const result = await this.getConfiguredModels();
      return result.providers?.flatMap(provider =>
        provider.models.map(model => ({
          id: `${provider.id}/${model.id}`,
          name: `${provider.id}/${model.id}`,
          custom_api_base: false
        }))
      ) || [];
    } catch {
      return [];
    }
  }
}