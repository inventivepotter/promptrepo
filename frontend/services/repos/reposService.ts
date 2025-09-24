import ReposApi from './api';
import { isErrorResponse, isStandardResponse } from '@/types/OpenApiResponse';
import { errorNotification } from '@/lib/notifications';
import type { components } from '@/types/generated/api';

import * as configuredReposData from './configuredRepos.json';
import * as availableReposData from './availableRepos.json';
const mockConfiguredRepos = configuredReposData as ConfiguredReposResponse;
const mockAvailableRepos = availableReposData as RepositoryList;

type RepositoryList = components['schemas']['RepositoryList'];
type ConfiguredReposResponse = components['schemas']['ConfiguredReposResponse'];

export class ReposService {
  /**
   * Get all configured repositories for the authenticated user/organization
   * @returns The configured repositories
   */
  static async getConfiguredRepos(): Promise<ConfiguredReposResponse> {
    try {
      const response = await ReposApi.getConfiguredRepos();
      
      if (isErrorResponse(response)) {
        errorNotification(
          response.title || 'Repository Sync Failed',
          response.detail || 'Unable to load configured repositories from server. Using local data.'
        );
        return mockConfiguredRepos;
      }
 
      if (isStandardResponse(response) && response.data) {
        return response.data as ConfiguredReposResponse;
      }

      // Fallback for unexpected response types, though ideally this path shouldn't be hit
      // if the API contract is correctly followed.
      errorNotification(
        'Unexpected Data Format',
        'Received an unexpected response format from the server. Using local data.'
      );
      return mockConfiguredRepos;
    } catch (error: unknown) {
      console.error('Failed to load configured repositories:', error);
      errorNotification(
        'Connection Error',
        'Unable to connect to repository service. Using local data.'
      );
      return mockConfiguredRepos;
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
        errorNotification(
          response.title || 'Failed to Load Repositories',
          response.detail || 'Unable to load available repositories.'
        );
        return mockAvailableRepos;
      }

      if (isStandardResponse(response) && response.data) {
        return response.data;
      }

      // Fallback for unexpected response types
      errorNotification(
        'Unexpected Data Format',
        'Received an unexpected response format from the server. Using local data.'
      );
      return mockAvailableRepos;
    } catch (error: unknown) {
      console.error('Failed to load repositories:', error);
      errorNotification(
        'Connection Error',
        'Unable to connect to repository service. Using local data.'
      );
      return mockAvailableRepos;
    }
  }
}