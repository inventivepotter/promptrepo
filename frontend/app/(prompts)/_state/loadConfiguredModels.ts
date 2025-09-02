import { getConfiguredModels } from "../_lib/getConfiguredModels";
import { LOCAL_STORAGE_KEYS } from "@/utils/localStorageConstants";
import { PromptsState } from "../_types/PromptState";
import { LLMProvider } from "@/types/LLMProvider";

// Cache selected models to localStorage for fallback (primary source is now API via getConfiguredModels)
export const persistConfiguredModelsToBrowserStorage = (configuredModels: PromptsState['configuredModels']) => {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(LOCAL_STORAGE_KEYS.CONFIGURED_MODELS, JSON.stringify(configuredModels));
  }
};

export const getConfiguredModelsFromBrowserStorage = (): PromptsState['configuredModels'] => {
  if (typeof window !== "undefined") {
    const saved = window.localStorage.getItem(LOCAL_STORAGE_KEYS.CONFIGURED_MODELS);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        // Ensure the result is an array of LLMProvider objects
        if (Array.isArray(parsed) && parsed.length > 0) {
          // Check if each item is a valid LLMProvider (either nested or flattened structure)
          const isValidLLMProviderArray = parsed.every((item: unknown) =>
            item && typeof item === 'object' &&
            'id' in item && typeof item.id === 'string' &&
            'name' in item && typeof item.name === 'string' &&
            (
              // Check for nested structure (original API format)
              ('models' in item && Array.isArray(item.models) &&
               item.models.every((model: unknown) =>
                 model && typeof model === 'object' &&
                 'id' in model && typeof (model as { id: unknown }).id === 'string' &&
                 'name' in model && typeof (model as { name: unknown }).name === 'string')) ||
              // Check for flattened structure (processed format with custom_api_base)
              ('custom_api_base' in item && typeof item.custom_api_base === 'boolean')
            )
          );
          
          if (isValidLLMProviderArray) {
            return parsed as LLMProvider[];
          }
        }
      } catch (parseError) {
      }
    }
  }
  return [];
};

// Load configured models from localStorage with API fallback
export const loadConfiguredModels = async (): Promise<PromptsState['configuredModels']> => {
  try {
    const localModels = getConfiguredModelsFromBrowserStorage();
    if (localModels && localModels.length > 0) {
      return localModels;
    }

    // If no valid data in localStorage, try to get from API
    const apiModels = await getConfiguredModels();

    // Update localStorage cache with fresh API data
    if (apiModels.length > 0) {
      persistConfiguredModelsToBrowserStorage(apiModels);
    }
    return apiModels;
  } catch (error) {
    return getConfiguredModelsFromBrowserStorage();
  }
};