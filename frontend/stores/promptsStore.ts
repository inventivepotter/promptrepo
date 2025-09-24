import { localStorage } from '@/lib/localStorage';

// Storage keys for this module
const STORE_NAME = {
  PROMPTS_DATA: 'promptsData'
} as const;

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

/**
 * Store prompts to localStorage
 * @param prompts - Array of prompt objects to store
 */
export const storePrompts = (prompts: Prompt[]): void => {
  // Convert Prompt objects to PromptJson for storage (convert dates to strings)
  const promptsJson: PromptJson[] = prompts.map(prompt => ({
    ...prompt,
    created_at: prompt.created_at.toISOString(),
    updated_at: prompt.updated_at.toISOString(),
  }));
  localStorage.set(STORE_NAME.PROMPTS_DATA, promptsJson);
};

/**
 * Get prompts from localStorage
 * @returns Array of prompt objects from storage
 */
export const getPromptsFromStorage = (): Prompt[] => {
  const saved = localStorage.get<PromptJson[]>(STORE_NAME.PROMPTS_DATA);
  if (saved && Array.isArray(saved)) {
    try {
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
    } catch (parseError) {
      console.warn("Invalid prompt data found in localStorage", parseError);
    }
  }
  return [];
};

/**
 * Clear prompts from localStorage
 */
export const clearPromptsFromStorage = (): void => {
  localStorage.clear(STORE_NAME.PROMPTS_DATA);
};

/**
 * Update a specific prompt in storage
 * @param promptId - ID of the prompt to update
 * @param updatedPrompt - Updated prompt object
 */
export const updatePromptInStorage = (promptId: string, updatedPrompt: Prompt): void => {
  const currentPrompts = getPromptsFromStorage();
  const updatedPrompts = currentPrompts.map(prompt =>
    prompt.id === promptId ? { ...updatedPrompt, updated_at: new Date() } : prompt
  );
  storePrompts(updatedPrompts);
};

/**
 * Add a new prompt to storage
 * @param newPrompt - New prompt object to add
 */
export const addPromptToStorage = (newPrompt: Prompt): void => {
  const currentPrompts = getPromptsFromStorage();
  const promptWithTimestamps = {
    ...newPrompt,
    created_at: new Date(),
    updated_at: new Date()
  };
  const updatedPrompts = [...currentPrompts, promptWithTimestamps];
  storePrompts(updatedPrompts);
};

/**
 * Remove a prompt from storage
 * @param promptId - ID of the prompt to remove
 */
export const removePromptFromStorage = (promptId: string): void => {
  const currentPrompts = getPromptsFromStorage();
  const updatedPrompts = currentPrompts.filter(prompt => prompt.id !== promptId);
  storePrompts(updatedPrompts);
};

/**
 * Check if a specific prompt exists in storage
 * @param promptId - ID of the prompt to check
 * @returns boolean indicating if prompt exists
 */
export const isPromptInStorage = (promptId: string): boolean => {
  const currentPrompts = getPromptsFromStorage();
  return currentPrompts.some(prompt => prompt.id === promptId);
};

/**
 * Get a specific prompt from storage
 * @param promptId - ID of the prompt to get
 * @returns Prompt if found, null otherwise
 */
export const getPromptFromStorage = (promptId: string): Prompt | null => {
  const currentPrompts = getPromptsFromStorage();
  return currentPrompts.find(prompt => prompt.id === promptId) || null;
};

/**
 * Search prompts in storage by name
 * @param searchTerm - Term to search for in prompt names
 * @returns Array of matching prompts
 */
export const searchPromptsInStorage = (searchTerm: string): Prompt[] => {
  const currentPrompts = getPromptsFromStorage();
  return currentPrompts.filter(prompt =>
    prompt.name.toLowerCase().includes(searchTerm.toLowerCase())
  );
};
