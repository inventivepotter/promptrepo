import { Configuration } from '@/types/Configuration'
import mockConfigData from './config.json'

export function fetchMockConfigData(): Configuration {
  return mockConfigData as Configuration;
};

export const fetchConfigFromBackend = async (): Promise<Configuration> => {
  try {
    await new Promise(resolve => setTimeout(resolve, 100));
    // TODO: Fetch config from backend API
    return fetchMockConfigData();
  } catch (error) {
    // Return default data as fallback
    return {
        hostingType: "",
        githubClientId: "",
        githubClientSecret: "",
        llmConfigs: [],
      } as Configuration;
  }
};