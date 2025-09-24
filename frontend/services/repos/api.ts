import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

/**
 * Repositories API client
 * All methods return OpenAPI-formatted responses
 */
type RepositoryList = components['schemas']['RepositoryList'];
type ConfiguredReposResponse = components['schemas']['ConfiguredReposResponse'];

export default class ReposApi {
  /**
   * Get all available repositories for the authenticated user
   * @returns OpenAPI response with available repositories
   */
  static async getAvailableRepos(): Promise<OpenApiResponse<RepositoryList>> {
    return await httpClient.get<RepositoryList>('/api/v0/repos/available');
  }

  /**
   * Get all configured repositories for the authenticated user/organization
   * @returns OpenAPI response with configured repositories
   */
  static async getConfiguredRepos(): Promise<OpenApiResponse<ConfiguredReposResponse>> {
    return await httpClient.get<ConfiguredReposResponse>('/api/v0/repos/configured');
  }
}
