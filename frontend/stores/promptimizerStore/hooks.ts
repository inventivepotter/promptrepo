/**
 * Custom hooks for the Promptimizer store.
 */
import { usePromptOptimizerStore } from './store';

// State hooks
export const usePromptOptimizerIsOpen = () =>
  usePromptOptimizerStore((state) => state.isOpen);

export const usePromptOptimizerExpectsUserMessage = () =>
  usePromptOptimizerStore((state) => state.expectsUserMessage);

export const usePromptOptimizerMessages = () =>
  usePromptOptimizerStore((state) => state.messages);

export const usePromptOptimizerOptimizedPrompt = () =>
  usePromptOptimizerStore((state) => state.optimizedPrompt);

export const usePromptOptimizerIsLoading = () =>
  usePromptOptimizerStore((state) => state.isLoading);

export const usePromptOptimizerError = () =>
  usePromptOptimizerStore((state) => state.error);

// Computed hooks
export const usePromptOptimizerHasOptimizedPrompt = () =>
  usePromptOptimizerStore((state) => state.optimizedPrompt !== null);

export const usePromptOptimizerHasMessages = () =>
  usePromptOptimizerStore((state) => state.messages.length > 0);

export const usePromptOptimizerHasAssistantMessage = () =>
  usePromptOptimizerStore((state) =>
    state.messages.some((m) => m.role === 'assistant')
  );

// Actions hook
export const usePromptOptimizerActions = () => {
  const store = usePromptOptimizerStore();

  return {
    openDialog: store.openDialog,
    closeDialog: store.closeDialog,
    setExpectsUserMessage: store.setExpectsUserMessage,
    sendMessage: store.sendMessage,
    applyPrompt: store.applyPrompt,
    clearConversation: store.clearConversation,
    setError: store.setError,
    reset: store.reset,
  };
};

// Combined state and actions hook for convenience
export const usePromptOptimizer = () => {
  const isOpen = usePromptOptimizerIsOpen();
  const expectsUserMessage = usePromptOptimizerExpectsUserMessage();
  const messages = usePromptOptimizerMessages();
  const optimizedPrompt = usePromptOptimizerOptimizedPrompt();
  const isLoading = usePromptOptimizerIsLoading();
  const error = usePromptOptimizerError();
  const hasOptimizedPrompt = usePromptOptimizerHasOptimizedPrompt();
  const hasAssistantMessage = usePromptOptimizerHasAssistantMessage();
  const actions = usePromptOptimizerActions();

  return {
    // State
    isOpen,
    expectsUserMessage,
    messages,
    optimizedPrompt,
    isLoading,
    error,
    hasOptimizedPrompt,
    hasAssistantMessage,

    // Actions
    ...actions,
  };
};
