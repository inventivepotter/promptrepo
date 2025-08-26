import { Repo } from "@/types/Repo";
import availableRepos from './availableRepos.json'
import { reposApi } from './api/reposApi';
import { errorNotification } from '@/lib/notifications';
import { ApiResponse } from "@/types/ApiResponse";
import logger from '@/lib/logger';

export function getAvailableRepos(): Repo[] {
  return availableRepos.repos;
}

export async function getAvailableReposWithApi(): Promise<Repo[]> {
  try {
    const result: ApiResponse<Repo[]> = await reposApi.getAvailableRepos();
    
    if (!result.success) {
      // Log the API error with context for debugging
      logger.error({
        error: result.error,
        message: result.message,
        statusCode: 'statusCode' in result ? result.statusCode : undefined
      }, 'Failed to fetch available repositories from API');
      
      // Show user-friendly notification
      errorNotification(
        result.error || 'Repository Sync Failed',
        result.message || 'Unable to load latest repositories from server. Using local data.'
      );
      
      return availableRepos.repos;
    }

    if (!result.data || result.data.length === 0) {
      logger.warn('API returned empty repository data');
      
      errorNotification(
        'No Repositories Available',
        'The server returned no repositories. Using local data.'
      );

      return availableRepos.repos;
    }

    // Log successful API call (info level - less noisy than notifications)
    logger.info(`Successfully fetched ${result.data.length} repositories from API`);
    
    return result.data;
  } catch (error: unknown) {
    // Enhanced error handling with proper type checking
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    const errorName = error instanceof Error ? error.name : 'UnknownError';
    
    // Log the unexpected error with context
    logger.error({
      error: errorName,
      message: errorMessage,
      stack: error instanceof Error ? error.stack : undefined
    }, 'Unexpected error fetching available repositories');
    
    // Show user-friendly notification
    errorNotification(
      'Connection Error',
      'Unable to connect to repository service. Using local data.'
    );
    
    return availableRepos.repos;
  }
}
