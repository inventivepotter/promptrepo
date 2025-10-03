// Chat store actions implementation
import type { StateCreator } from '@/lib/zustand';
import { chatService } from '@/services/llm/chat/chatService';
import type { ChatStore, ChatActions, ChatSession } from './types';
import type { ChatMessage } from '@/app/(prompts)/_types/ChatState';
import type { ChatCompletionOptions } from '@/types/Chat';

// Helper function to generate unique IDs
const generateId = () => `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

// Create all chat actions as a single StateCreator
export const createChatActions: StateCreator<ChatStore, [], [], ChatActions> = (set, get, api) => ({
  // Session Management
  createSession: (title?, modelConfig?, systemPrompt?) => {
    const sessionId = `session-${generateId()}`;
    const now = new Date();
    
    const newSession: ChatSession = {
      id: sessionId,
      title: title || `Chat ${now.toLocaleDateString()} ${now.toLocaleTimeString()}`,
      messages: [],
      createdAt: now,
      updatedAt: now,
      modelConfig: modelConfig || get().defaultModelConfig,
      systemPrompt,
    };
    
    set((draft) => {
      draft.sessions.unshift(newSession);
      draft.currentSessionId = sessionId;
      draft.messages = [];
      draft.inputMessage = '';
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/create-session');
    
    return newSession;
  },
  
  deleteSession: (sessionId: string) => {
    set((draft) => {
      draft.sessions = draft.sessions.filter(s => s.id !== sessionId);
      if (draft.currentSessionId === sessionId) {
        draft.currentSessionId = draft.sessions[0]?.id || null;
        draft.messages = draft.sessions[0]?.messages || [];
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/delete-session');
  },
  
  setCurrentSession: (sessionId: string | null) => {
    const session = sessionId ? get().sessions.find(s => s.id === sessionId) : null;
    
    set((draft) => {
      draft.currentSessionId = sessionId;
      draft.messages = session?.messages || [];
      draft.editingMessageId = null;
      draft.editingContent = '';
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/set-current-session');
  },
  
  updateSessionTitle: (sessionId: string, title: string) => {
    set((draft) => {
      const session = draft.sessions.find(s => s.id === sessionId);
      if (session) {
        session.title = title;
        session.updatedAt = new Date();
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/update-session-title');
  },
  
  clearAllSessions: () => {
    set((draft) => {
      draft.sessions = [];
      draft.currentSessionId = null;
      draft.messages = [];
      draft.inputMessage = '';
      draft.totalTokensUsed = 0;
      draft.totalCost = 0;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/clear-all-sessions');
  },
  
  // Message Operations
  sendMessage: async (content: string, options = {}) => {
    const state = get();
    let currentSession = state.sessions.find(s => s.id === state.currentSessionId);
    
    // Create a new session if none exists
    if (!currentSession) {
      currentSession = get().createSession();
    }
    
    // Create user message
    const userMessage = chatService.createUserMessage(content);
    
    set((draft) => {
      draft.isSending = true;
      draft.error = null;
      draft.inputMessage = '';
      
      // Add user message to current session
      const session = draft.sessions.find(s => s.id === draft.currentSessionId);
      if (session) {
        session.messages.push(userMessage);
        session.updatedAt = new Date();
      }
      draft.messages.push(userMessage);
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/send-message-start');
    
    try {
      // Prepare completion options
      const modelConfig = options.modelConfig 
        ? { ...currentSession.modelConfig, ...options.modelConfig }
        : currentSession.modelConfig;
        
      const completionOptions: ChatCompletionOptions = {
        provider: modelConfig.provider,
        model: modelConfig.model,
        temperature: modelConfig.temperature,
        max_tokens: modelConfig.max_tokens,
        top_p: modelConfig.top_p,
        frequency_penalty: modelConfig.frequency_penalty,
        presence_penalty: modelConfig.presence_penalty,
        stream: options.onStream !== undefined,
      };
      
      // Convert messages to OpenAI format
      const messages = chatService.toOpenAIMessages(get().messages);
      
      // Send to chat service
      const assistantMessage = await chatService.sendChatCompletion(
        messages,
        options.promptId,
        completionOptions,
        options.systemPrompt || currentSession.systemPrompt
      );
      
      if (assistantMessage) {
        set((draft) => {
          // Add assistant message to session
          const session = draft.sessions.find(s => s.id === draft.currentSessionId);
          if (session) {
            session.messages.push(assistantMessage);
            session.updatedAt = new Date();
          }
          draft.messages.push(assistantMessage);
          
          // Update statistics if available
          if (assistantMessage.usage) {
            draft.totalTokensUsed += assistantMessage.usage.total_tokens || 0;
          }
          if (assistantMessage.cost) {
            draft.totalCost += assistantMessage.cost;
          }
          
          draft.isSending = false;
        // @ts-expect-error - Immer middleware supports 3 params
        }, false, 'chat/send-message-success');
      } else {
        throw new Error('Failed to get response from chat service');
      }
    } catch (error) {
      set((draft) => {
        draft.error = error instanceof Error ? error.message : 'Failed to send message';
        draft.isSending = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'chat/send-message-error');
    }
  },
  
  addMessage: (message: ChatMessage) => {
    set((draft) => {
      const session = draft.sessions.find(s => s.id === draft.currentSessionId);
      if (session) {
        session.messages.push(message);
        session.updatedAt = new Date();
      }
      draft.messages.push(message);
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/add-message');
  },
  
  updateMessage: (messageId: string, updates: Partial<ChatMessage>) => {
    set((draft) => {
      const session = draft.sessions.find(s => s.id === draft.currentSessionId);
      if (session) {
        const messageIndex = session.messages.findIndex(m => m.id === messageId);
        if (messageIndex !== -1) {
          session.messages[messageIndex] = { ...session.messages[messageIndex], ...updates };
          session.updatedAt = new Date();
        }
      }
      
      const messageIndex = draft.messages.findIndex(m => m.id === messageId);
      if (messageIndex !== -1) {
        draft.messages[messageIndex] = { ...draft.messages[messageIndex], ...updates };
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/update-message');
  },
  
  deleteMessage: (messageId: string) => {
    set((draft) => {
      const session = draft.sessions.find(s => s.id === draft.currentSessionId);
      if (session) {
        session.messages = session.messages.filter(m => m.id !== messageId);
        session.updatedAt = new Date();
      }
      draft.messages = draft.messages.filter(m => m.id !== messageId);
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/delete-message');
  },
  
  regenerateMessage: async (messageId: string) => {
    const state = get();
    const messageIndex = state.messages.findIndex(m => m.id === messageId);
    
    if (messageIndex === -1) return;
    
    // Find the last user message before this one
    const messagesBeforeThis = state.messages.slice(0, messageIndex);
    const lastUserMessage = [...messagesBeforeThis].reverse().find(m => m.role === 'user');
    
    if (!lastUserMessage) return;
    
    // Remove this message and all messages after it
    set((draft) => {
      draft.isRegenerating = true;
      draft.messages = draft.messages.slice(0, messageIndex);
      
      const session = draft.sessions.find(s => s.id === draft.currentSessionId);
      if (session) {
        session.messages = session.messages.slice(0, messageIndex);
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/regenerate-message-start');
    
    // Resend the last user message to get a new response
    try {
      await get().sendMessage(lastUserMessage.content);
      set((draft) => {
        draft.isRegenerating = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'chat/regenerate-message-success');
    } catch (error) {
      set((draft) => {
        draft.error = error instanceof Error ? error.message : 'Failed to regenerate message';
        draft.isRegenerating = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'chat/regenerate-message-error');
    }
  },
  
  clearMessages: () => {
    set((draft) => {
      const session = draft.sessions.find(s => s.id === draft.currentSessionId);
      if (session) {
        session.messages = [];
        session.updatedAt = new Date();
      }
      draft.messages = [];
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/clear-messages');
  },
  
  // Message Editing
  startEditingMessage: (messageId: string) => {
    const message = get().messages.find(m => m.id === messageId);
    if (message) {
      set((draft) => {
        draft.editingMessageId = messageId;
        draft.editingContent = message.content;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'chat/start-editing-message');
    }
  },
  
  cancelEditingMessage: () => {
    set((draft) => {
      draft.editingMessageId = null;
      draft.editingContent = '';
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/cancel-editing-message');
  },
  
  saveEditedMessage: async () => {
    const state = get();
    const { editingMessageId, editingContent } = state;
    
    if (!editingMessageId || !editingContent) return;
    
    const messageIndex = state.messages.findIndex(m => m.id === editingMessageId);
    if (messageIndex === -1) return;
    
    const editedMessage = state.messages[messageIndex];
    
    // Update the message content
    get().updateMessage(editingMessageId, { content: editingContent });
    
    // If it's a user message, regenerate the response
    if (editedMessage.role === 'user') {
      // Remove all messages after the edited message
      set((draft) => {
        draft.messages = draft.messages.slice(0, messageIndex + 1);
        const session = draft.sessions.find(s => s.id === draft.currentSessionId);
        if (session) {
          session.messages = session.messages.slice(0, messageIndex + 1);
        }
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'chat/save-edited-message-cleanup');
      
      // Send the edited message to get a new response
      await get().sendMessage(editingContent);
    }
    
    get().cancelEditingMessage();
  },
  
  setEditingContent: (content: string) => {
    set((draft) => {
      draft.editingContent = content;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/set-editing-content');
  },
  
  // Streaming
  startStreaming: (messageId: string) => {
    set((draft) => {
      draft.streaming = {
        isStreaming: true,
        streamingMessageId: messageId,
        streamingContent: '',
      };
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/start-streaming');
  },
  
  updateStreamingContent: (content: string) => {
    set((draft) => {
      draft.streaming.streamingContent = content;
      
      // Update the message content if streaming
      if (draft.streaming.streamingMessageId) {
        const messageIndex = draft.messages.findIndex(
          m => m.id === draft.streaming.streamingMessageId
        );
        if (messageIndex !== -1) {
          draft.messages[messageIndex].content = content;
        }
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/update-streaming-content');
  },
  
  stopStreaming: () => {
    set((draft) => {
      draft.streaming = {
        isStreaming: false,
        streamingMessageId: null,
        streamingContent: '',
      };
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/stop-streaming');
  },
  
  // Model Configuration
  setDefaultModelConfig: (config: Partial<ChatStore['defaultModelConfig']>) => {
    set((draft) => {
      draft.defaultModelConfig = { ...draft.defaultModelConfig, ...config };
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/set-default-model-config');
  },
  
  updateSessionModelConfig: (sessionId: string, config: Partial<ChatStore['defaultModelConfig']>) => {
    set((draft) => {
      const session = draft.sessions.find(s => s.id === sessionId);
      if (session) {
        session.modelConfig = { ...session.modelConfig, ...config };
        session.updatedAt = new Date();
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/update-session-model-config');
  },
  
  // System Prompts
  updateSessionSystemPrompt: (sessionId: string, systemPrompt: string) => {
    set((draft) => {
      const session = draft.sessions.find(s => s.id === sessionId);
      if (session) {
        session.systemPrompt = systemPrompt;
        session.updatedAt = new Date();
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/update-session-system-prompt');
  },
  
  // Input Management
  setInputMessage: (message: string) => {
    set((draft) => {
      draft.inputMessage = message;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/set-input-message');
  },
  
  clearInput: () => {
    set((draft) => {
      draft.inputMessage = '';
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/clear-input');
  },
  
  // Error Handling
  setError: (error: string | null) => {
    set((draft) => {
      draft.error = error;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/set-error');
  },
  
  clearError: () => {
    set((draft) => {
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/clear-error');
  },
  
  // Statistics
  updateStatistics: (tokensUsed: number, cost: number) => {
    set((draft) => {
      draft.totalTokensUsed += tokensUsed;
      draft.totalCost += cost;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/update-statistics');
  },
  
  // Utility
  exportSession: (sessionId: string) => {
    return get().sessions.find(s => s.id === sessionId) || null;
  },
  
  importSession: (session: ChatSession) => {
    set((draft) => {
      // Check if session already exists
      const existingIndex = draft.sessions.findIndex(s => s.id === session.id);
      if (existingIndex !== -1) {
        draft.sessions[existingIndex] = session;
      } else {
        draft.sessions.unshift(session);
      }
      draft.currentSessionId = session.id;
      draft.messages = session.messages;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/import-session');
  },
  
  // Reset
  reset: () => {
    set((draft) => {
      draft.sessions = [];
      draft.currentSessionId = null;
      draft.messages = [];
      draft.isLoading = false;
      draft.isSending = false;
      draft.isRegenerating = false;
      draft.isDeleting = false;
      draft.error = null;
      draft.streaming = {
        isStreaming: false,
        streamingMessageId: null,
        streamingContent: '',
      };
      draft.editingMessageId = null;
      draft.editingContent = '';
      draft.inputMessage = '';
      draft.totalTokensUsed = 0;
      draft.totalCost = 0;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/reset');
  },
});