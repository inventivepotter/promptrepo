import { Repo } from "@/types/Repo";
import * as availableReposData from './availableRepos.json'
import { reposApi } from './api/reposApi';
import { errorNotification } from '@/lib/notifications';
import { ApiResponse } from "@/types/ApiResponse";

const availableRepos = availableReposData as { repos: Repo[] };

export function getAvailableRepos(): Repo[] {
  return availableRepos.repos;
}

export async function getAvailableReposWithApi(): Promise<Repo[]> {
  try {
    const result: ApiResponse<Repo[]> = await reposApi.getAvailableRepos();
    
    if (!result.success) {
      
      // Show user-friendly notification
      errorNotification(
        result.error || 'Repository Sync Failed',
        result.message || 'Unable to load latest repositories from server. Using local data.'
      );
      // return Promise.reject({error: result.error, message: result.message});
      
      return availableRepos.repos;
    }

    if (!result.data || result.data.length === 0) {
      
      errorNotification(
        'No Repositories Available',
        'The server returned no repositories. Using local data.'
      );

      return availableRepos.repos;
    }

    
    return result.data;
  } catch (error: unknown) {
    
    // return Promise.reject(error);
    errorNotification(
      'Connection Error',
      'Unable to connect to repository service. Using local data.'
    );
    
    return availableRepos.repos;
  }
}