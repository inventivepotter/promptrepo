import { Repo } from "@/types/Repo";
import * as configuredReposData from './configuredRepos.json'
import { reposApi } from './api/reposApi';
import { errorNotification } from '@/lib/notifications';
import { ApiResponse } from "@/types/ApiResponse";
import { getHostingType } from '@/utils/hostingType';

const configuredRepos = configuredReposData as { repos: Repo[] };

export async function getConfiguredRepos(): Promise<Repo[]> {
  try {
    // Check hosting type to determine behavior
    const hostingType = await getHostingType();
    
    // For individual hosting type, repos edit won't be available - return empty
    if (hostingType === 'individual') {
      return [];
    }
    
    // For organization hosting type, call backend for GitHub repos
    const result: ApiResponse<Repo[]> = await reposApi.getConfiguredRepos();
    
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