import { localStorage } from '@/lib/localStorage';
import { LOCAL_STORAGE_KEYS } from '@/utils/localStorageConstants';

// Define Prompt types (using the actual types from the project)
interface Prompt {
  id: string;
  name: string;
  content?: string;
  created_at: Date;
  updated_at: Date;
  [key: string]: unknown;
}

interface PromptJson {
  id: string;
  name: string;
  content?: string;
  created_at: string;
  updated_at: string;
  [key: string]: unknown;
}

// Use the centralized storage keys
const STORE_NAME = LOCAL_STORAGE_KEYS;

/**
 * Core Storage Functions
 */

/**
 * Store prompts to localStorage
 * @param prompts - Array of prompt objects to store
 */
export const storePrompts = (prompts: Prompt[]): void => {
  try {
    if (typeof window === 'undefined') return;
    
    // Convert Prompt objects to PromptJson for storage (convert dates to strings)
    const promptsJson: PromptJson[] = prompts.map(prompt => ({
      ...prompt,
      created_at: prompt.created_at.toISOString(),
      updated_at: prompt.updated_at.toISOString(),
    }));
    
    localStorage.set(STORE_NAME.PROMPTS_DATA, promptsJson);
  } catch (error) {
    console.error('Failed to store prompts:', error);
    throw new Error('Failed to store prompts');
  }
};

/**
 * Get prompts from localStorage
 * @returns Array of prompt objects from storage
 */
export const getPrompts = (): Prompt[] => {
  try {
    if (typeof window === 'undefined') return [];
    
    const saved = localStorage.get<PromptJson[]>(STORE_NAME.PROMPTS_DATA);
    if (!saved || !Array.isArray(saved)) {
      return [];
    }
    
    const prompts = saved.map((p) => ({
      ...p,
      created_at: new Date(p.created_at),
      updated_at: new Date(p.updated_at),
    }));

    // Validate the data structure
    const isValidPromptArray = prompts.every((item: unknown): item is Prompt => {
      if (!item || typeof item !== 'object' || item === null) return false;
      const obj = item as Record<string, unknown>;
      return (
        'id' in obj && typeof obj.id === 'string' &&
        'name' in obj && typeof obj.name === 'string' &&
        'created_at' in obj && obj.created_at instanceof Date &&
        'updated_at' in obj && obj.updated_at instanceof Date
      );
    });
    
    if (isValidPromptArray) {
      return prompts as Prompt[];
    }
    
    console.warn('Invalid prompt data structure found in localStorage');
    return [];
  } catch (error) {
    console.error('Failed to get prompts:', error);
    return [];
  }
};

/**
 * Clear prompts from localStorage
 */
export const clearPrompts = (): void => {
  try {
    if (typeof window === 'undefined') return;
    localStorage.clear(STORE_NAME.PROMPTS_DATA);
  } catch (error) {
    console.error('Failed to clear prompts:', error);
  }
};

/**
 * CRUD Operations
 */

/**
 * Add a new prompt to storage
 * @param newPrompt - New prompt object to add
 */
export const addPrompt = (newPrompt: Prompt): void => {
  try {
    const currentPrompts = getPrompts();
    const promptWithTimestamps = {
      ...newPrompt,
      created_at: newPrompt.created_at || new Date(),
      updated_at: newPrompt.updated_at || new Date()
    };
    const updatedPrompts = [...currentPrompts, promptWithTimestamps];
    storePrompts(updatedPrompts);
  } catch (error) {
    console.error('Failed to add prompt:', error);
    throw new Error('Failed to add prompt');
  }
};

/**
 * Update a specific prompt in storage
 * @param promptId - ID of the prompt to update
 * @param updatedPrompt - Updated prompt object
 */
export const updatePrompt = (promptId: string, updatedPrompt: Prompt): void => {
  try {
    const currentPrompts = getPrompts();
    const updatedPrompts = currentPrompts.map(prompt =>
      prompt.id === promptId
        ? { ...updatedPrompt, updated_at: new Date() }
        : prompt
    );
    storePrompts(updatedPrompts);
  } catch (error) {
    console.error('Failed to update prompt:', error);
    throw new Error('Failed to update prompt');
  }
};

/**
 * Remove a prompt from storage
 * @param promptId - ID of the prompt to remove
 */
export const removePrompt = (promptId: string): void => {
  try {
    const currentPrompts = getPrompts();
    const updatedPrompts = currentPrompts.filter(prompt => prompt.id !== promptId);
    storePrompts(updatedPrompts);
  } catch (error) {
    console.error('Failed to remove prompt:', error);
    throw new Error('Failed to remove prompt');
  }
};

/**
 * Query Operations
 */

/**
 * Check if a specific prompt exists in storage
 * @param promptId - ID of the prompt to check
 * @returns boolean indicating if prompt exists
 */
export const hasPrompt = (promptId: string): boolean => {
  try {
    const currentPrompts = getPrompts();
    return currentPrompts.some(prompt => prompt.id === promptId);
  } catch (error) {
    console.error('Failed to check prompt existence:', error);
    return false;
  }
};

/**
 * Get a specific prompt from storage
 * @param promptId - ID of the prompt to get
 * @returns Prompt if found, null otherwise
 */
export const getPrompt = (promptId: string): Prompt | null => {
  try {
    const currentPrompts = getPrompts();
    return currentPrompts.find(prompt => prompt.id === promptId) || null;
  } catch (error) {
    console.error('Failed to get prompt:', error);
    return null;
  }
};

/**
 * Search prompts in storage by name
 * @param searchTerm - Term to search for in prompt names
 * @returns Array of matching prompts
 */
export const searchPrompts = (searchTerm: string): Prompt[] => {
  try {
    const currentPrompts = getPrompts();
    return currentPrompts.filter(prompt =>
      prompt.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  } catch (error) {
    console.error('Failed to search prompts:', error);
    return [];
  }
};

/**
 * Backward Compatibility Exports
 * These exports maintain backward compatibility with the old naming convention
 */
export const getPromptsFromStorage = getPrompts;
export const clearPromptsFromStorage = clearPrompts;
export const addPromptToStorage = addPrompt;
export const updatePromptInStorage = updatePrompt;
export const removePromptFromStorage = removePrompt;
export const isPromptInStorage = hasPrompt;
export const getPromptFromStorage = getPrompt;
export const searchPromptsInStorage = searchPrompts;
