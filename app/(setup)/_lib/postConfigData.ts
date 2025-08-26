import { SetupData } from '../_state/configState';

export interface PostConfigDataResponse {
  success: boolean;
  message?: string;
  error?: string;
}

/**
 * Reads configuration data from localStorage
 */
export const getConfigDataFromStorage = (): SetupData | null => {
  if (typeof window === 'undefined') return null;
  
  const savedConfig = localStorage.getItem('interviewSetupData');
  if (!savedConfig) return null;

  try {
    const configData = JSON.parse(savedConfig);
    
    // Validate the structure
    if (typeof configData === 'object' &&
        configData !== null &&
        typeof configData.hostingType === 'string' &&
        typeof configData.githubClientId === 'string' &&
        typeof configData.githubClientSecret === 'string' &&
        Array.isArray(configData.llmConfigs) &&
        typeof configData.currentStep === 'object') {
      return configData;
    }
    
    return null;
  } catch {
    return null;
  }
};

/**
 * Posts configuration data directly without reading from localStorage
 * This is the optimized version that avoids localStorage reads
 */
export const postConfigData = async (configData: SetupData): Promise<PostConfigDataResponse> => {
  try {
    if (!configData) {
      return {
        success: false,
        error: 'No configuration data provided'
      };
    }

    // Prepare the data for posting
    const payload = {
      hostingType: configData.hostingType,
      githubClientId: configData.githubClientId,
      githubClientSecret: configData.githubClientSecret,
      llmConfigs: configData.llmConfigs,
      timestamp: new Date().toISOString(),
    };
    
    console.log('Posting config data to backend:', payload);
    
    //TODO: Post the data to the server endpoint
    return {
      success: true,
      message: 'Configuration saved successfully',
    };
  } catch (error) {
    console.error('Error posting configuration data:', error);
    
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to post configuration data',
    };
  }
};

/**
 * Debounced version for frequent updates
 * Delays the API call to avoid excessive requests during rapid field changes
 */
let debounceTimer: NodeJS.Timeout | null = null;
//TODO: More thoughts ?
export const postConfigDataDebounced = (configData: SetupData, delay: number = 500): void => {
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }
  
  debounceTimer = setTimeout(() => {
    postConfigData(configData);
  }, delay);
};

/**
 * Posts configuration data by first reading from localStorage, then posting
 * This is the legacy version - prefer postConfigData with direct data passing
 */
export const postStoredConfigData = async (): Promise<PostConfigDataResponse> => {
  try {
    // Get configuration from localStorage
    const configData = getConfigDataFromStorage();
    
    if (!configData) {
      return {
        success: false,
        error: 'No configuration data found in storage'
      };
    }

    // Use the optimized version
    return await postConfigData(configData);
  } catch (error) {
    console.error('Error posting configuration data:', error);
    
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to post configuration data',
    };
  }
};