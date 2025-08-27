import { Prompt } from '@/types/Prompt';
import { LOCAL_STORAGE_KEYS } from '../_lib/localStorageConstants';
import { getPrompts } from '../_lib/getPrompts';
import { PromptJson } from '../_types/PromptState';

// Cache prompts to localStorage for fallback (primary source is now API via getPrompts)
export const persistPromptsToBrowserStorage = (prompts: Prompt[]) => {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(LOCAL_STORAGE_KEYS.PROMPTS_DATA, JSON.stringify(prompts));
  }
};

export const getPromptsFromBrowserStorage = (): Prompt[] => {
  if (typeof window !== "undefined") {
    const saved = window.localStorage.getItem(LOCAL_STORAGE_KEYS.PROMPTS_DATA);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);

        const casted = (parsed as PromptJson[]).map((p) => ({
          ...p,
          created_at: new Date(p.created_at),
          updated_at: new Date(p.updated_at),
        }))

        // Ensure the result is an array of Prompt objects
        if (Array.isArray(casted) && casted.length > 0) {
          // Check if each item is of type Prompt
          const isValidPromptArray = casted.every((item: Prompt): item is Prompt =>
            item && typeof item === 'object' &&
            'id' in item && typeof item.id === 'string' &&
            'name' in item && typeof item.name === 'string' &&
            'created_at' in item && item.created_at instanceof Date &&
            'updated_at' in item && item.updated_at instanceof Date
          );
          
          if (isValidPromptArray) {
            return casted;
          }
          console.log("Invalid prompt data found in localStorage 1", parsed);
        }
      } catch (parseError) {
          console.log("Invalid prompt data found in localStorage 2");
        // TODO: Implement logger and log it
      }
    }
  }
  return [];
};

// Load prompts from localStorage with API fallback
export const loadPrompts = async (): Promise<Prompt[]> => {
  try {
    // First check localStorage for existing prompts
    const localPrompts = getPromptsFromBrowserStorage();
    if (localPrompts && localPrompts.length > 0) {
      return localPrompts;
    }

    // If no valid data in localStorage, try to get from API
    const apiPrompts = await getPrompts();

    // Update localStorage cache with fresh API data
    if (apiPrompts.length > 0) {
      persistPromptsToBrowserStorage(apiPrompts);
    }
    return apiPrompts;
  } catch (error) {
    return getPromptsFromBrowserStorage();
  }
};
