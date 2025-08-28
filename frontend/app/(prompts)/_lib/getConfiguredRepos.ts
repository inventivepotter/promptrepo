import { Repo } from "@/types/Repo";
import configuredRepos from './configuredRepos.json'
import { reposApi } from './api/reposApi';
import { errorNotification } from '@/lib/notifications';
import { ApiResponse } from "@/types/ApiResponse";

export async function getConfiguredRepos(userId?: string): Promise<Repo[]> {
  try {
    const result: ApiResponse<Repo[]> = await reposApi.getConfiguredRepos(userId);
    
    if (!result.success) {
      
      errorNotification(
        result.error || 'Repository Sync Failed',
        result.message || 'Unable to load configured repositories from server. Using local data.'
      );
      // return Promise.reject({error: result.error, message: result.message});
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
    // return Promise.reject(error);
    errorNotification(
      'Connection Error',
      'Unable to connect to repository service. Using local data.'
    );
    
    return configuredRepos.repos;
  }
}
