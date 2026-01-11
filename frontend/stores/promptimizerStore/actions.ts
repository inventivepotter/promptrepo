/**
 * Actions for the Promptimizer store.
 */
import type { StateCreator } from '@/lib/zustand';
import { promptOptimizerApi } from '@/services/promptimizer/api';
import type { PromptOptimizerStore, PromptOptimizerActions, PromptOptimizerMessage } from './types';
import { initialPromptOptimizerState } from './state';
import { isErrorResponse } from '@/types/OpenApiResponse';

/**
 * Generate a unique message ID.
 */
const generateMessageId = (): string => {
  return `msg_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`;
};

export const createPromptOptimizerActions: StateCreator<
  PromptOptimizerStore,
  [],
  [],
  PromptOptimizerActions
> = (set, get) => ({
  // Dialog management
  openDialog: () => {
    set((draft) => {
      draft.isOpen = true;
    }, false, 'promptimizer/open-dialog');
  },

  closeDialog: () => {
    set((draft) => {
      draft.isOpen = false;
    }, false, 'promptimizer/close-dialog');
  },

  // Configuration
  setExpectsUserMessage: (value: boolean) => {
    set((draft) => {
      draft.expectsUserMessage = value;
    }, false, 'promptimizer/set-expects-user-message');
  },

  // Conversation
  sendMessage: async (content: string, provider: string, model: string, currentPrompt?: string) => {
    const userMessage: PromptOptimizerMessage = {
      id: generateMessageId(),
      role: 'user',
      content,
      timestamp: new Date(),
    };

    // Add user message and start loading
    set((draft) => {
      draft.messages.push(userMessage);
      draft.isLoading = true;
      draft.error = null;
    }, false, 'promptimizer/send-message-start');

    try {
      const state = get();

      // Build conversation history for multi-turn (exclude the message we just added)
      const conversationHistory = state.messages.slice(0, -1).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      // Call API
      const result = await promptOptimizerApi.optimize({
        idea: content,
        provider,
        model,
        expects_user_message: state.expectsUserMessage,
        conversation_history: conversationHistory.length > 0 ? conversationHistory : undefined,
        current_prompt: currentPrompt && currentPrompt.trim() ? currentPrompt : undefined,
      });

      if (isErrorResponse(result)) {
        throw new Error(result.detail || result.title || 'Optimization failed');
      }

      if (result.data) {
        const assistantMessage: PromptOptimizerMessage = {
          id: generateMessageId(),
          role: 'assistant',
          content: result.data.optimized_prompt,
          timestamp: new Date(),
        };

        set((draft) => {
          draft.messages.push(assistantMessage);
          draft.optimizedPrompt = result.data?.optimized_prompt || null;
          draft.isLoading = false;
        }, false, 'promptimizer/send-message-success');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      set((draft) => {
        draft.error = errorMessage;
        draft.isLoading = false;
      }, false, 'promptimizer/send-message-error');
    }
  },

  applyPrompt: () => {
    return get().optimizedPrompt;
  },

  clearConversation: () => {
    set((draft) => {
      draft.messages = [];
      draft.optimizedPrompt = null;
      draft.error = null;
    }, false, 'promptimizer/clear-conversation');
  },

  // State management
  setError: (error: string | null) => {
    set((draft) => {
      draft.error = error;
    }, false, 'promptimizer/set-error');
  },

  reset: () => {
    set(() => ({
      ...initialPromptOptimizerState,
    }), false, 'promptimizer/reset');
  },
});
