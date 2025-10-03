// Storage configuration for chat store
import { createLocalStorage } from '@/lib/zustand';
import type { ChatStore } from './types';

/**
 * Storage configuration for chat store persistence
 * Stores chat sessions, messages, and user preferences
 */
export const chatPersistConfig = {
  ...createLocalStorage('chat-store'),
  // Only persist essential chat data
  partialize: (state: ChatStore) => ({
    // Persist all sessions with their messages
    sessions: state.sessions,
    currentSessionId: state.currentSessionId,
    
    // Persist default model configuration
    defaultModelConfig: state.defaultModelConfig,
    
    // Persist statistics
    totalTokensUsed: state.totalTokensUsed,
    totalCost: state.totalCost,
    
    // Don't persist:
    // - UI states (isLoading, isSending, etc.)
    // - Temporary states (streaming, editing)
    // - Error states
    // - Input message (should be cleared on reload)
  }),
  // Allow manual hydration if needed
  skipHydration: false,
  // Version for migration support
  version: 1,
  // Migration function for future schema changes
  migrate: (persistedState: unknown, version: number) => {
    if (version === 0) {
      // Handle migration from version 0 to 1
      // Example: Convert old session format to new format
    }
    return persistedState;
  },
};