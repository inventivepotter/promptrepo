/**
 * Initial state for the Promptimizer store.
 */
import type { PromptOptimizerState } from './types';

export const initialPromptOptimizerState: PromptOptimizerState = {
  // Dialog state
  isOpen: false,

  // Configuration
  expectsUserMessage: false,

  // Conversation
  messages: [],
  optimizedPrompt: null,

  // Loading state
  isLoading: false,
  error: null,
};
