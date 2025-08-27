import { getConfiguredRepos } from "../_lib/getConfiguredRepos";
import { LOCAL_STORAGE_KEYS } from "../../../utils/localStorageConstants";
import { PromptsState } from "../_types/PromptState";
import { Repo } from "@/types/Repo";

export const persistConfiguredReposToBrowserStorage = (configuredRepos: PromptsState['configuredRepos']) => {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(LOCAL_STORAGE_KEYS.CONFIGURED_REPOS, JSON.stringify(configuredRepos));
  }
};

export const getConfiguredReposFromBrowserStorage = (): PromptsState['configuredRepos'] => {
  if (typeof window !== "undefined") {
    const saved = window.localStorage.getItem(LOCAL_STORAGE_KEYS.CONFIGURED_REPOS);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          const isValidRepoArray = parsed.every((item: Repo): item is Repo =>
            item && typeof item === 'object' &&
            'id' in item && typeof item.id === 'string' &&
            'name' in item && typeof item.name === 'string'
          );
          
          if (isValidRepoArray) {
            return parsed;
          }
        }
      } catch (parseError) {
      }
    }
  }
  return [];
};

export const loadConfiguredRepos = async (userId?: string): Promise<PromptsState['configuredRepos']> => {
  try {
    const localRepos = getConfiguredReposFromBrowserStorage();
    if (localRepos && localRepos.length > 0) {
      return localRepos;
    }

    const apiRepos = await getConfiguredRepos(userId);

    if (apiRepos.length > 0) {
      persistConfiguredReposToBrowserStorage(apiRepos);
    }
    return apiRepos;
  } catch (error) {
    return getConfiguredReposFromBrowserStorage();
  }
};
