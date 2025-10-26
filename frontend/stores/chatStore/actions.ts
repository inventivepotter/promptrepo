// Chat store actions implementation
import type { StateCreator } from '@/lib/zustand';
import { chatService } from '@/services/llm/chat/chatService';
import type { ChatStore, ChatActions, ChatSession } from './types';
import type { ChatMessage, Tool } from '@/app/(prompts)/_types/ChatState';
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
  sendMessage: async (content: string, options: { systemPrompt?: string; modelConfig?: Partial<ChatStore['defaultModelConfig']>; promptId?: string; repoName?: string; onStream?: (content: string) => void } = {}) => {
    // Get initial state at the start
    const initialState = get();
    let currentSession = initialState.sessions.find(s => s.id === initialState.currentSessionId);
    
    // Create a new session if none exists
    if (!currentSession) {
      currentSession = get().createSession();
    }
    
    // Create system message if systemPrompt is provided and it's the first message
    const isFirstMessage = initialState.messages.length === 0;
    let systemMessage = null;
    if (options.systemPrompt && isFirstMessage) {
      systemMessage = chatService.createSystemMessage(options.systemPrompt);
    }
    
    // Create user message only if content is provided
    const userMessage = content.trim() ? chatService.createUserMessage(content) : null;
    
    set((draft) => {
      draft.isSending = true;
      draft.error = null;
      draft.inputMessage = '';
      
      // Add system message if needed
      if (systemMessage) {
        const session = draft.sessions.find(s => s.id === draft.currentSessionId);
        if (session) {
          session.messages.push(systemMessage);
        }
        draft.messages.push(systemMessage);
      }
      
      // Add user message to current session only if it exists
      if (userMessage) {
        const session = draft.sessions.find(s => s.id === draft.currentSessionId);
        if (session) {
          session.messages.push(userMessage);
          session.updatedAt = new Date();
        }
        draft.messages.push(userMessage);
      }
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/send-message-start');
    
    try {
      // Get fresh state and session for model config
      const freshState = get();
      const freshSession = freshState.sessions.find(s => s.id === freshState.currentSessionId);
      
      // Prepare completion options using fresh session data
      const modelConfig = options.modelConfig
        ? { ...(freshSession?.modelConfig || freshState.defaultModelConfig), ...options.modelConfig }
        : (freshSession?.modelConfig || freshState.defaultModelConfig);
        
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
      
      // Get selected tools and convert to OpenAI function format
      const selectedToolIds = get().selectedTools;
      const availableTools = get().availableTools;
      const toolsForCompletion = selectedToolIds.length > 0
        ? selectedToolIds.map(toolId => {
            const tool = availableTools.find(t => t.id === toolId);
            if (!tool) return null;
            return {
              type: 'function',
              function: {
                name: tool.id,
                description: tool.description,
                parameters: {
                  type: 'object',
                  properties: {},
                  required: []
                }
              }
            };
          }).filter(Boolean)
        : undefined;
      
      // Send to chat service
      const assistantMessage = await chatService.sendChatCompletion(
        messages,
        options.promptId,
        completionOptions,
        options.systemPrompt || currentSession.systemPrompt,
        toolsForCompletion,
        options.repoName
      );
      
      if (assistantMessage) {
        set((draft) => {
          const session = draft.sessions.find(s => s.id === draft.currentSessionId);
          
          // If there are tool responses, this means the backend executed the tool loop
          // We need to reconstruct the message order: tool_calls message -> tool responses -> final answer
          if (assistantMessage.tool_responses && Array.isArray(assistantMessage.tool_responses) && assistantMessage.tool_responses.length > 0) {
            // Create the initial assistant message with tool_calls (if tool_calls exist in the response)
            // The backend should have returned tool_calls in the message even after executing the loop
            if (assistantMessage.tool_calls && assistantMessage.tool_calls.length > 0) {
              const toolCallMessage = chatService.createAssistantMessage('', assistantMessage.tool_calls);
              if (session) {
                session.messages.push(toolCallMessage);
                session.updatedAt = new Date();
              }
              draft.messages.push(toolCallMessage);
            }
            
            // Add tool response messages
            for (const toolResponse of assistantMessage.tool_responses) {
              const toolMessage = chatService.createToolMessage(
                toolResponse.content,
                toolResponse.tool_call_id || ''
              );
              
              if (session) {
                session.messages.push(toolMessage);
              }
              draft.messages.push(toolMessage);
            }
            
            // Create final answer message (without tool_calls)
            const finalAnswerMessage = chatService.createAssistantMessage(assistantMessage.content);
            // Copy over metadata
            if (assistantMessage.usage) finalAnswerMessage.usage = assistantMessage.usage;
            if (assistantMessage.cost) finalAnswerMessage.cost = assistantMessage.cost;
            if (assistantMessage.model) finalAnswerMessage.model = assistantMessage.model;
            if (assistantMessage.inferenceTimeMs) finalAnswerMessage.inferenceTimeMs = assistantMessage.inferenceTimeMs;
            
            if (session) {
              session.messages.push(finalAnswerMessage);
              session.updatedAt = new Date();
            }
            draft.messages.push(finalAnswerMessage);
          } else {
            // No tool loop executed, just add the assistant message as-is
            if (session) {
              session.messages.push(assistantMessage);
              session.updatedAt = new Date();
            }
            draft.messages.push(assistantMessage);
          }
          
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
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'chat/reset');
  },
});