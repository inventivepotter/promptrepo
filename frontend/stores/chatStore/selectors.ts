import { ChatStore, ChatSession } from './types';
import { ChatMessage, Tool } from '@/app/prompts/_types/ChatState';
import { ModelConfig } from './types';

// Session Selectors
export const selectSessions = (state: ChatStore): ChatSession[] => state.sessions;
export const selectCurrentSessionId = (state: ChatStore): string | null => state.currentSessionId;
export const selectCurrentSession = (state: ChatStore): ChatSession | null => 
  state.sessions.find(s => s.id === state.currentSessionId) || null;

// Message Selectors
export const selectMessages = (state: ChatStore): ChatMessage[] => state.messages;
export const selectLastMessage = (state: ChatStore): ChatMessage | null => 
  state.messages.length > 0 ? state.messages[state.messages.length - 1] : null;
export const selectUserMessages = (state: ChatStore): ChatMessage[] =>
  state.messages.filter(m => m.role === 'user');
export const selectAssistantMessages = (state: ChatStore): ChatMessage[] =>
  state.messages.filter(m => m.role === 'assistant');

// Loading State Selectors
export const selectIsLoading = (state: ChatStore): boolean => state.isLoading;
export const selectIsSending = (state: ChatStore): boolean => state.isSending;
export const selectIsRegenerating = (state: ChatStore): boolean => state.isRegenerating;
export const selectIsDeleting = (state: ChatStore): boolean => state.isDeleting;
export const selectIsProcessing = (state: ChatStore): boolean =>
  state.isLoading || state.isSending || state.isRegenerating || state.isDeleting;

// Streaming Selectors
export const selectIsStreaming = (state: ChatStore): boolean => state.streaming.isStreaming;
export const selectStreamingMessageId = (state: ChatStore): string | null => 
  state.streaming.streamingMessageId;
export const selectStreamingContent = (state: ChatStore): string => state.streaming.streamingContent;

// Editing Selectors
export const selectEditingMessageId = (state: ChatStore): string | null => state.editingMessageId;
export const selectEditingContent = (state: ChatStore): string => state.editingContent;
export const selectIsEditingMessage = (state: ChatStore): boolean => state.editingMessageId !== null;

// Model Configuration Selectors
export const selectDefaultModelConfig = (state: ChatStore): ModelConfig => state.defaultModelConfig;
export const selectCurrentSessionModelConfig = (state: ChatStore): ModelConfig | null => {
  const currentSession = selectCurrentSession(state);
  return currentSession?.modelConfig || null;
};

// Input Selectors
export const selectInputMessage = (state: ChatStore): string => state.inputMessage;
export const selectHasInput = (state: ChatStore): boolean => state.inputMessage.trim().length > 0;

// Error Selector
export const selectError = (state: ChatStore): string | null => state.error;
export const selectHasError = (state: ChatStore): boolean => state.error !== null;

// Statistics Selectors
export const selectTotalTokensUsed = (state: ChatStore): number => state.totalTokensUsed;
export const selectTotalCost = (state: ChatStore): number => state.totalCost;
export const selectSessionTokensUsed = (state: ChatStore): number => {
  const currentSession = selectCurrentSession(state);
  if (!currentSession) return 0;
  
  return currentSession.messages.reduce((total, msg) => {
    return total + (msg.usage?.total_tokens || 0);
  }, 0);
};
export const selectSessionCost = (state: ChatStore): number => {
  const currentSession = selectCurrentSession(state);
  if (!currentSession) return 0;
  
  return currentSession.messages.reduce((total, msg) => {
    return total + (msg.cost || 0);
  }, 0);
};

// Computed Selectors
export const selectSessionById = (id: string) => (state: ChatStore): ChatSession | undefined =>
  state.sessions.find(session => session.id === id);

export const selectMessageById = (id: string) => (state: ChatStore): ChatMessage | undefined =>
  state.messages.find(message => message.id === id);

export const selectSessionCount = (state: ChatStore): number => state.sessions.length;
export const selectMessageCount = (state: ChatStore): number => state.messages.length;

export const selectHasSessions = (state: ChatStore): boolean => state.sessions.length > 0;
export const selectHasMessages = (state: ChatStore): boolean => state.messages.length > 0;

export const selectCanSendMessage = (state: ChatStore): boolean =>
  !state.isSending && !state.isRegenerating && state.inputMessage.trim().length > 0;

export const selectRecentSessions = (count: number = 5) => (state: ChatStore): ChatSession[] =>
  state.sessions.slice(0, count);

export const selectSessionsByDateRange = (startDate: Date, endDate: Date) => (state: ChatStore): ChatSession[] =>
  state.sessions.filter(session => 
    session.createdAt >= startDate && session.createdAt <= endDate
  );

export const selectMessagesWithTokenUsage = (state: ChatStore): ChatMessage[] =>
  state.messages.filter(m => m.usage && m.usage.total_tokens);

export const selectAverageResponseTime = (state: ChatStore): number | null => {
  const assistantMessages = selectAssistantMessages(state);
  const messagesWithInferenceTime = assistantMessages.filter(m => m.inferenceTimeMs);
  
  if (messagesWithInferenceTime.length === 0) return null;
  
  const totalTime = messagesWithInferenceTime.reduce(
    (sum, msg) => sum + (msg.inferenceTimeMs || 0),
    0
  );
  
  return totalTime / messagesWithInferenceTime.length;
};

export const selectSessionSummary = (state: ChatStore) => {
  const currentSession = selectCurrentSession(state);
  if (!currentSession) return null;
  
  return {
    id: currentSession.id,
    title: currentSession.title,
    messageCount: currentSession.messages.length,
    userMessageCount: currentSession.messages.filter(m => m.role === 'user').length,
    assistantMessageCount: currentSession.messages.filter(m => m.role === 'assistant').length,
    createdAt: currentSession.createdAt,
    updatedAt: currentSession.updatedAt,
    modelConfig: currentSession.modelConfig,
    systemPrompt: currentSession.systemPrompt,
    totalTokens: selectSessionTokensUsed(state),
    totalCost: selectSessionCost(state),
  };
};

export const selectSessionsWithStats = (state: ChatStore) => {
  return state.sessions.map(session => {
    const messageCount = session.messages.length;
    const userMessageCount = session.messages.filter(m => m.role === 'user').length;
    const assistantMessageCount = session.messages.filter(m => m.role === 'assistant').length;
    const totalTokens = session.messages.reduce((sum, msg) => sum + (msg.usage?.total_tokens || 0), 0);
    const totalCost = session.messages.reduce((sum, msg) => sum + (msg.cost || 0), 0);
    
    return {
      ...session,
      stats: {
        messageCount,
        userMessageCount,
        assistantMessageCount,
        totalTokens,
        totalCost,
      },
    };
  });
};

export const selectIsSessionActive = (sessionId: string) => (state: ChatStore): boolean =>
  state.currentSessionId === sessionId;

export const selectCanRegenerateLastMessage = (state: ChatStore): boolean => {
  const lastMessage = selectLastMessage(state);
  return lastMessage !== null && lastMessage.role === 'assistant' && !state.isRegenerating;
};

// Tools Selectors
export const selectAvailableTools = (state: ChatStore): Tool[] => state.availableTools;
export const selectSelectedTools = (state: ChatStore): string[] => state.selectedTools;
export const selectSelectedToolObjects = (state: ChatStore): Tool[] =>
  state.availableTools.filter(tool => state.selectedTools.includes(tool.id));
export const selectHasSelectedTools = (state: ChatStore): boolean => state.selectedTools.length > 0;
export const selectIsToolSelected = (toolId: string) => (state: ChatStore): boolean =>
  state.selectedTools.includes(toolId);

// Token Calculation Selectors
export const selectTotalInputTokens = (state: ChatStore): number => {
  return state.messages.reduce((total, message) => {
    return total + (message.usage?.prompt_tokens || 0);
  }, 0);
};

export const selectTotalOutputTokens = (state: ChatStore): number => {
  return state.messages.reduce((total, message) => {
    return total + (message.usage?.completion_tokens || 0);
  }, 0);
};

export const selectTokenStats = (state: ChatStore) => ({
  totalInput: selectTotalInputTokens(state),
  totalOutput: selectTotalOutputTokens(state),
  total: selectTotalInputTokens(state) + selectTotalOutputTokens(state),
});