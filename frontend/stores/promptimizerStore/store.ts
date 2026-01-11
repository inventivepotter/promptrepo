/**
 * Promptimizer store implementation.
 *
 * This store manages the state for the AI-powered prompt optimization feature.
 */
import { create } from 'zustand';
import { devtools, immer } from '@/lib/zustand';
import { createPromptOptimizerActions } from './actions';
import { initialPromptOptimizerState } from './state';
import type { PromptOptimizerStore } from './types';

// Create the promptimizer store with middleware
export const usePromptOptimizerStore = create<PromptOptimizerStore>()(
  devtools(
    immer((set, get, api) => ({
      // Initial state
      ...initialPromptOptimizerState,

      // Actions
      ...createPromptOptimizerActions(set, get, api),
    })),
    {
      name: 'promptimizer-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

export default usePromptOptimizerStore;
