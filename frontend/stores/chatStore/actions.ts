// Chat store actions implementation
import type { StateCreator } from '@/lib/zustand';
import { chatService } from '@/services/llm/chat/chatService';
import { SharedChatApi } from '@/services/sharedChat';
import type { SharedChatMessage } from '@/services/sharedChat';
import type { ChatStore, ChatActions, ChatSession } from './types';
import type { ChatMessage, Tool } from '@/app/prompts/_types/ChatState';
import type { components } from '@/types/generated/api';
import { ResponseStatus } from '@/types/OpenApiResponse';

type PromptMeta = components['schemas']['PromptMeta'];
type MessageSchema = components['schemas']['UserMessageSchema'] | components['schemas']['AIMessageSchema'] | components['schemas']['SystemMessageSchema'] | components['schemas']['ToolMessageSchema'];

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
  sendMessage: async (content: string, options: { promptMeta?: PromptMeta; onStream?: (content: string) => void } = {}) => {
    // Get initial state at the start
    const initialState = get();
    let currentSession = initialState.sessions.find(s => s.id === initialState.currentSessionId);
    
    // Create a new session if none exists
    if (!currentSession) {
      currentSession = get().createSession();
    }
    
    // Validate that we have promptMeta
    if (!options.promptMeta) {
      set((draft) => {
        draft.error = 'No prompt metadata provided';
        draft.isSending = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'chat/send-message-error');
      return;
    }
    
    // Create system message if systemPrompt is in promptMeta and it's the first message
    const isFirstMessage = initialState.messages.length === 0;
    let systemMessage = null;
    if (options.promptMeta.prompt.prompt && isFirstMessage) {
      systemMessage = chatService.createSystemMessage(options.promptMeta.prompt.prompt);
    }
    
    // Create user message only if content is provided
    const userMessage = content.trim() ? chatService.createUserMessage(content) : null;
    
    set((draft) => {
      draft.isSending = true;
      draft.error = null;
      draft.inputMessage = '';

      const session = draft.sessions.find(s => s.id === draft.currentSessionId);

      // Update session's modelConfig from promptMeta on first message
      if (session && isFirstMessage && options.promptMeta?.prompt) {
        const prompt = options.promptMeta.prompt;
        session.modelConfig = {
          ...session.modelConfig,
          provider: prompt.provider || session.modelConfig.provider,
          model: prompt.model || session.modelConfig.model,
          temperature: prompt.temperature ?? session.modelConfig.temperature,
          max_tokens: prompt.max_tokens ?? session.modelConfig.max_tokens,
        };
      }

      // Add system message if needed
      if (systemMessage) {
        if (session) {
          session.messages.push(systemMessage);
        }
        draft.messages.push(systemMessage);
      }

      // Add user message to current session only if it exists
      if (userMessage) {
        if (session) {
          session.messages.push(userMessage);
          session.updatedAt = new Date();
        }
        draft.messages.push(userMessage);
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/send-message-start');
    
    try {
      // Convert messages to MessageSchema format for backend
      const currentMessages = get().messages;
      console.log('[sendMessage] Current messages count:', currentMessages.length);
      console.log('[sendMessage] Current messages:', currentMessages.map(m => ({ role: m.role, content: m.content?.substring(0, 50) })));

      const messageSchemas: MessageSchema[] = currentMessages.map(msg => {
        if (msg.role === 'user') {
          return {
            role: 'user' as const,
            content: msg.content,
            timestamp: msg.timestamp?.toISOString() || null,
            metadata: null,
            user_id: null
          };
        } else if (msg.role === 'assistant') {
          return {
            role: 'assistant' as const,
            content: msg.content,
            timestamp: msg.timestamp?.toISOString() || null,
            metadata: null,
            model: null,
            tool_calls: msg.tool_calls && Array.isArray(msg.tool_calls) && msg.tool_calls.length > 0 && 'id' in msg.tool_calls[0] && 'function' in msg.tool_calls[0]
              ? msg.tool_calls.map(tc => {
                  const toolCall = tc as { id: string; type: 'function'; function: { name: string; arguments: string; } };
                  return {
                    id: toolCall.id,
                    name: toolCall.function.name,
                    arguments: typeof toolCall.function.arguments === 'string' ? JSON.parse(toolCall.function.arguments) : toolCall.function.arguments
                  };
                })
              : null,
            finish_reason: null,
            token_usage: null
          };
        } else if (msg.role === 'system') {
          return {
            role: 'system' as const,
            content: msg.content,
            timestamp: msg.timestamp?.toISOString() || null,
            metadata: null,
            priority: null
          };
        } else if (msg.role === 'tool') {
          return {
            role: 'tool' as const,
            content: msg.content,
            timestamp: msg.timestamp?.toISOString() || null,
            metadata: null,
            tool_call_id: msg.tool_call_id || '',
            tool_name: '',
            is_error: false
          };
        }
        // Default fallback (shouldn't reach here)
        return {
          role: 'user' as const,
          content: msg.content,
          timestamp: msg.timestamp?.toISOString() || null,
          metadata: null,
          user_id: null
        };
      });
      
      // Send to chat service with PromptMeta
      const assistantMessage = await chatService.sendChatCompletion(
        options.promptMeta,
        messageSchemas
      );
      
      if (assistantMessage) {
        set((draft) => {
          const session = draft.sessions.find(s => s.id === draft.currentSessionId);

          // If there are tool calls, this means the backend executed the tool loop
          // toolCalls now contains MessageSchema objects: AIMessageSchema with tool_calls + ToolMessageSchema with results
          if (assistantMessage.toolCalls && Array.isArray(assistantMessage.toolCalls) && assistantMessage.toolCalls.length > 0) {
            // New format: toolCalls is MessageSchema[]
            for (const toolMessageSchema of assistantMessage.toolCalls) {
              let chatMessage: ChatMessage;

              if (toolMessageSchema.role === 'assistant') {
                // This is the AI message with tool calls
                const aiMessageSchema = toolMessageSchema as components['schemas']['AIMessageSchema'];
                chatMessage = chatService.createAssistantMessage(
                  aiMessageSchema.content || '',
                  aiMessageSchema.tool_calls ? aiMessageSchema.tool_calls.map(tc => ({
                    id: tc.id,
                    type: 'function' as const,
                    function: {
                      name: tc.name,
                      arguments: typeof tc.arguments === 'string' ? tc.arguments : JSON.stringify(tc.arguments)
                    }
                  })) : undefined
                );
              } else if (toolMessageSchema.role === 'tool') {
                // This is a tool response message
                const toolMessageSchema_ = toolMessageSchema as components['schemas']['ToolMessageSchema'];
                chatMessage = chatService.createToolMessage(
                  toolMessageSchema_.content,
                  toolMessageSchema_.tool_call_id || ''
                );
              } else {
                // Fallback - shouldn't happen
                continue;
              }

              // Copy timestamp if available
              if (toolMessageSchema.timestamp) {
                chatMessage.timestamp = new Date(toolMessageSchema.timestamp);
              }

              if (session) {
                session.messages.push(chatMessage);
                session.updatedAt = new Date();
              }
              draft.messages.push(chatMessage);
            }
          }

          // Add the final assistant message
          if (session) {
            session.messages.push(assistantMessage.message);
            session.updatedAt = new Date();
          }
          draft.messages.push(assistantMessage.message);

          // Update statistics if available
          if (assistantMessage.message.usage) {
            draft.totalTokensUsed += assistantMessage.message.usage.total_tokens || 0;
          }
          if (assistantMessage.message.cost) {
            draft.totalCost += assistantMessage.message.cost;
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
    // Get fresh state
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
    // Get fresh state
    let state = get();
    const { editingMessageId, editingContent } = state;
    
    if (!editingMessageId || !editingContent) return;
    
    const messageIndex = state.messages.findIndex(m => m.id === editingMessageId);
    if (messageIndex === -1) return;
    
    const editedMessage = state.messages[messageIndex];
    
    // Update the message content
    get().updateMessage(editingMessageId, { content: editingContent });
    
    // Refresh state after update
    state = get();
    
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
  
  // Template Variables Management
  setTemplateVariable: (name: string, value: string) => {
    set((draft) => {
      draft.templateVariables[name] = value;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/set-template-variable');
  },
  
  clearTemplateVariables: () => {
    set((draft) => {
      draft.templateVariables = {};
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/clear-template-variables');
  },
  
  // Tools Management
  setAvailableTools: (tools: Tool[]) => {
    set((draft) => {
      draft.availableTools = tools;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/set-available-tools');
  },
  
  setSelectedTools: (toolIds: string[]) => {
    set((draft) => {
      draft.selectedTools = toolIds;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/set-selected-tools');
  },
  
  toggleTool: (toolId: string) => {
    set((draft) => {
      const index = draft.selectedTools.indexOf(toolId);
      if (index === -1) {
        draft.selectedTools.push(toolId);
      } else {
        draft.selectedTools.splice(index, 1);
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/toggle-tool');
  },
  
  clearSelectedTools: () => {
    set((draft) => {
      draft.selectedTools = [];
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/clear-selected-tools');
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
      draft.templateVariables = {};
      draft.availableTools = [];
      draft.selectedTools = [];
      draft.totalTokensUsed = 0;
      draft.totalCost = 0;
      draft.isSharing = false;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/reset');
  },

  // Sharing
  shareCurrentSession: async (title?: string, includeSystemPrompt: boolean = true) => {
    const state = get();
    const { currentSessionId, sessions, messages, totalTokensUsed, totalCost } = state;

    if (!currentSessionId || messages.length === 0) {
      return null;
    }

    const currentSession = sessions.find(s => s.id === currentSessionId);
    if (!currentSession) {
      return null;
    }

    set((draft) => {
      draft.isSharing = true;
      draft.error = null;
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/share-start');

    try {
      // Filter out system messages if not including them
      const messagesToShare = includeSystemPrompt
        ? messages
        : messages.filter(msg => msg.role !== 'system');

      // Convert messages to SharedChatMessage format
      const sharedMessages: SharedChatMessage[] = messagesToShare.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp?.toISOString() || new Date().toISOString(),
        usage: msg.usage ? {
          prompt_tokens: msg.usage.prompt_tokens,
          completion_tokens: msg.usage.completion_tokens,
          total_tokens: msg.usage.total_tokens,
          reasoning_tokens: msg.usage.reasoning_tokens,
        } : undefined,
        cost: msg.cost,
        inference_time_ms: msg.inferenceTimeMs,
        tool_calls: msg.tool_calls && Array.isArray(msg.tool_calls) ?
          msg.tool_calls.map(tc => {
            if ('function' in tc) {
              return {
                id: tc.id,
                name: tc.function.name,
                arguments: typeof tc.function.arguments === 'string'
                  ? JSON.parse(tc.function.arguments)
                  : tc.function.arguments,
              };
            }
            return {
              id: '',
              name: '',
              arguments: {},
            };
          }).filter(tc => tc.id !== '') : undefined,
      }));

      // Use custom title if provided, otherwise fall back to session title
      const chatTitle = title || currentSession.title;

      const response = await SharedChatApi.createSharedChat({
        title: chatTitle,
        messages: sharedMessages,
        model_config_data: {
          provider: currentSession.modelConfig.provider,
          model: currentSession.modelConfig.model,
          temperature: currentSession.modelConfig.temperature,
          max_tokens: currentSession.modelConfig.max_tokens,
        },
        total_tokens: totalTokensUsed,
        total_cost: totalCost,
      });

      set((draft) => {
        draft.isSharing = false;
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'chat/share-success');

      if (response.status === ResponseStatus.SUCCESS && response.data) {
        return {
          shareId: response.data.share_id,
          shareUrl: response.data.share_url,
        };
      }

      throw new Error('Failed to create shared chat');
    } catch (error) {
      set((draft) => {
        draft.isSharing = false;
        draft.error = error instanceof Error ? error.message : 'Failed to share chat';
      // @ts-expect-error - Immer middleware supports 3 params
      }, false, 'chat/share-error');
      return null;
    }
  },
});