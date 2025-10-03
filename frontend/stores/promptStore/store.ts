// Main prompt store implementation
import { create } from 'zustand';
import { devtools, persist, immer } from '@/lib/zustand';
import { createPromptActions } from './actions';
import { initialPromptState } from './state';
import { promptPersistConfig } from './storage';
import type { PromptStore } from './types';

// Create the prompt store with middleware
export const usePromptStore = create<PromptStore>()(
  devtools(
    persist(
      immer((set, get, api) => ({
        // Initial state
        ...initialPromptState,
        
        // Actions
        ...createPromptActions(set, get, api),
      })),
      promptPersistConfig
    ),
    {
      name: 'prompt-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

// Export the store instance for direct access if needed
export default usePromptStore;