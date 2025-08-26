import { Repo } from "@/types/Repo";
import configuredRepos from './configuredRepos.json'
import { reposApi } from './api/reposApi';
import { errorNotification } from '@/lib/notifications';
import { ApiResponse } from "@/types/ApiResponse";
import logger from '@/lib/logger';

export async function getConfiguredRepos(): Promise<Repo[]> {
  try {
    const result: ApiResponse<Repo[]> = await reposApi.getConfiguredRepos();
    
    if (!result.success) {
      // Log the API error with context for debugging
      logger.error({
        error: result.error,
        message: result.message,
        statusCode: 'statusCode' in result ? result.statusCode : undefined
      }, 'Failed to fetch configured repositories from API');
      
      // Show user-friendly notification
      errorNotification(
        result.error || 'Repository Sync Failed',
        result.message || 'Unable to load configured repositories from server. Using local data.'
      );
      
      return configuredRepos.repos;
    }

    if (!result.data || result.data.length === 0) {
      logger.warn('API returned empty configured repository data');
      
      errorNotification(
        'No Configured Repositories',
        'The server returned no configured repositories. Using local data.'
      );

      return configuredRepos.repos;
    }

    // Log successful API call (info level - less noisy than notifications)
    logger.info(`Successfully fetched ${result.data.length} configured repositories from API`);
    
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
    }, 'Unexpected error fetching configured repositories');
    
    // Show user-friendly notification
    errorNotification(
      'Connection Error',
      'Unable to connect to repository service. Using local data.'
    );
    
    return configuredRepos.repos;
  }
}
