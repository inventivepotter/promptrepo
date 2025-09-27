import ReposApi from './api';
import { isErrorResponse, isStandardResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';


type RepositoryList = components['schemas']['RepositoryList'];
type ConfiguredReposResponse = components['schemas']['ConfiguredReposResponse'];
type RepositoryBranchesResponse = components['schemas']['RepositoryBranchesResponse'];

export class ReposService {
  /**
   * Get all configured repositories for the authenticated user/organization
   * @returns The configured repositories
   */
  static async getConfiguredRepos(): Promise<ConfiguredReposResponse> {
    try {
      const response = await ReposApi.getConfiguredRepos();
      
      if (isErrorResponse(response)) {
        throw response;

      }

      if (!isStandardResponse(response) || !response.data) {
        throw response;
      }

      return response.data as ConfiguredReposResponse;
    } catch (error: unknown) {
      throw error;
    }
  }

  /**
   * Get all available repositories for the authenticated user
   * @returns The available repositories
   */
  static async getAvailableRepos(): Promise<RepositoryList> {
    try {
      const response = await ReposApi.getAvailableRepos();
      
      // Handle error responses
      if (isErrorResponse(response)) {
        throw response;
      }

      if (!isStandardResponse(response) || !response.data) {
        throw response;
      }

      return response.data;
    } catch (error: unknown) {
      throw error;
    }
  }

  /**
   * Get branches for a specific repository
   * @param owner The repository owner
   * @param repo The repository name
   * @returns The repository branches
   */
  static async getBranches(owner: string, repo: string): Promise<RepositoryBranchesResponse> {
    try {
      const response = await ReposApi.getBranches(owner, repo);
      
      if (isErrorResponse(response)) {
        throw response;
      }

      if (!isStandardResponse(response) || !response.data) {
        throw response;
      }

      return response.data;
    } catch (error: unknown) {
      throw error;
    }
  }
}