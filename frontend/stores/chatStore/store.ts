// Main chat store implementation
import { create } from 'zustand';
import { devtools, persist, immer } from '@/lib/zustand';
import { createChatActions } from './actions';
import { initialChatState } from './state';
import { chatPersistConfig } from './storage';
import type { ChatStore } from './types';

// Create the chat store with middleware
export const useChatStore = create<ChatStore>()(
  devtools(
    persist(
      immer((set, get, api) => ({
        // Initial state
        ...initialChatState,
        
        // Actions
        ...createChatActions(set, get, api),
      })),
      chatPersistConfig
    ),
    {
      name: 'chat-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

// Export the store instance for direct access if needed
export default useChatStore;