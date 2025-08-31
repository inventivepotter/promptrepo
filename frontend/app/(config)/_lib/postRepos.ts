import { Repo } from '@/types/Repo';
import { reposApi } from './api/reposApi';
import { errorNotification, successNotification } from '@/lib/notifications';

export const postRepos = async (repos: Repo[]): Promise<Repo[]> => {
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));

    const result = await reposApi.updateRepos(repos);

    if (!result.success) {
      errorNotification(
        result.error || 'Repository Configuration Save Failed',
        result.message || 'Unable to save repository configuration on server. Changes may not be saved.'
      );

      return repos;
    }

    successNotification(
      'Repository Configuration Saved',
      'Your repository settings have been successfully saved.'
    );

    return result.data.repos;
  } catch (error: unknown) {
    errorNotification(
      'Connection Error',
      'Unable to connect to repository configuration service. Changes may not be saved.'
    );
    return repos;
  }
};