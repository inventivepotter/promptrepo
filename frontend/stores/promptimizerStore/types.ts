/**
 * Type definitions for the Promptimizer store.
 */

export interface PromptOptimizerMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface PromptOptimizerState {
  // Dialog state
  isOpen: boolean;

  // Configuration
  expectsUserMessage: boolean;

  // Conversation
  messages: PromptOptimizerMessage[];
  optimizedPrompt: string | null;

  // Loading state
  isLoading: boolean;
  error: string | null;
}

export interface PromptOptimizerActions {
  // Dialog management
  openDialog: () => void;
  closeDialog: () => void;

  // Configuration
  setExpectsUserMessage: (value: boolean) => void;

  // Conversation
  sendMessage: (content: string, provider: string, model: string, currentPrompt?: string) => Promise<void>;
  applyPrompt: () => string | null;
  clearConversation: () => void;

  // State management
  setError: (error: string | null) => void;
  reset: () => void;
}

export interface PromptOptimizerStore extends PromptOptimizerState, PromptOptimizerActions {}
