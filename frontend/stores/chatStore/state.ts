// Initial state for Chat Store
import type { ChatState } from './types';

export const initialChatState: ChatState = {
  // Sessions
  sessions: [],
  currentSessionId: null,
  
  // Messages (current session's messages)
  messages: [],
  
  // UI States
  isLoading: false,
  isSending: false,
  isRegenerating: false,
  isDeleting: false,
  error: null,
  
  // Streaming
  streaming: {
    isStreaming: false,
    streamingMessageId: null,
    streamingContent: '',
  },
  
  // Message editing
  editingMessageId: null,
  editingContent: '',
  
  // Default model configuration for new sessions
  defaultModelConfig: {
    provider: 'openai',
    model: 'gpt-4',
    temperature: 0.7,
    max_tokens: undefined,
    top_p: undefined,
    frequency_penalty: undefined,
    presence_penalty: undefined,
  },
  
  // Input state
  inputMessage: '',
  
  // Statistics
  totalTokensUsed: 0,
  totalCost: 0,
};