import { Repo } from "@/types/Repo";
import configuredRepos from './configuredRepos.json'
import { reposApi } from './api/reposApi';
import { errorNotification } from '@/lib/notifications';
import { ApiResponse } from "@/types/ApiResponse";

export async function getConfiguredRepos(): Promise<Repo[]> {
  try {
    const result: ApiResponse<Repo[]> = await reposApi.getConfiguredRepos();
    
    if (!result.success) {
      
      // Show user-friendly notification
      errorNotification(
        result.error || 'Repository Sync Failed',
        result.message || 'Unable to load configured repositories from server. Using local data.'
      );
      
      return configuredRepos.repos;
    }

    if (!result.data || result.data.length === 0) {
      
      errorNotification(
        'No Configured Repositories',
        'The server returned no configured repositories. Using local data.'
      );

      return configuredRepos.repos;
    }

    
    return result.data;
  } catch (error: unknown) {
    // Enhanced error handling with proper type checking
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    const errorName = error instanceof Error ? error.name : 'UnknownError';
    
    
    // Show user-friendly notification
    errorNotification(
      errorName || 'Connection Error',
      errorMessage || 'Unable to connect to repository service. Using local data.'
    );
    
    return configuredRepos.repos;
  }
}
