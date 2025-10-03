import { useChatStore } from './store';
import {
  selectSessions,
  selectCurrentSessionId,
  selectCurrentSession,
  selectMessages,
  selectLastMessage,
  selectUserMessages,
  selectAssistantMessages,
  selectIsLoading,
  selectIsSending,
  selectIsRegenerating,
  selectIsDeleting,
  selectIsProcessing,
  selectIsStreaming,
  selectStreamingMessageId,
  selectStreamingContent,
  selectEditingMessageId,
  selectEditingContent,
  selectIsEditingMessage,
  selectDefaultModelConfig,
  selectCurrentSessionModelConfig,
  selectInputMessage,
  selectHasInput,
  selectError,
  selectHasError,
  selectTotalTokensUsed,
  selectTotalCost,
  selectSessionTokensUsed,
  selectSessionCost,
  selectSessionById,
  selectMessageById,
  selectSessionCount,
  selectMessageCount,
  selectHasSessions,
  selectHasMessages,
  selectCanSendMessage,
  selectRecentSessions,
  selectSessionsByDateRange,
  selectMessagesWithTokenUsage,
  selectAverageResponseTime,
  selectSessionSummary,
  selectSessionsWithStats,
  selectIsSessionActive,
  selectCanRegenerateLastMessage,
} from './selectors';

// Session Hooks
export const useSessions = () => useChatStore(selectSessions);
export const useCurrentSessionId = () => useChatStore(selectCurrentSessionId);
export const useCurrentSession = () => useChatStore(selectCurrentSession);
export const useSessionById = (id: string) => useChatStore(selectSessionById(id));
export const useSessionCount = () => useChatStore(selectSessionCount);
export const useHasSessions = () => useChatStore(selectHasSessions);
export const useRecentSessions = (count: number = 5) => useChatStore(selectRecentSessions(count));
export const useSessionsByDateRange = (startDate: Date, endDate: Date) => 
  useChatStore(selectSessionsByDateRange(startDate, endDate));
export const useSessionSummary = () => useChatStore(selectSessionSummary);
export const useSessionsWithStats = () => useChatStore(selectSessionsWithStats);
export const useIsSessionActive = (sessionId: string) => useChatStore(selectIsSessionActive(sessionId));

// Message Hooks
export const useMessages = () => useChatStore(selectMessages);
export const useLastMessage = () => useChatStore(selectLastMessage);
export const useUserMessages = () => useChatStore(selectUserMessages);
export const useAssistantMessages = () => useChatStore(selectAssistantMessages);
export const useMessageById = (id: string) => useChatStore(selectMessageById(id));
export const useMessageCount = () => useChatStore(selectMessageCount);
export const useHasMessages = () => useChatStore(selectHasMessages);
export const useMessagesWithTokenUsage = () => useChatStore(selectMessagesWithTokenUsage);
export const useCanRegenerateLastMessage = () => useChatStore(selectCanRegenerateLastMessage);

// Loading State Hooks
export const useIsLoading = () => useChatStore(selectIsLoading);
export const useIsSending = () => useChatStore(selectIsSending);
export const useIsRegenerating = () => useChatStore(selectIsRegenerating);
export const useIsDeleting = () => useChatStore(selectIsDeleting);
export const useIsProcessing = () => useChatStore(selectIsProcessing);

// Streaming Hooks
export const useIsStreaming = () => useChatStore(selectIsStreaming);
export const useStreamingMessageId = () => useChatStore(selectStreamingMessageId);
export const useStreamingContent = () => useChatStore(selectStreamingContent);

// Editing Hooks
export const useEditingMessageId = () => useChatStore(selectEditingMessageId);
export const useEditingContent = () => useChatStore(selectEditingContent);
export const useIsEditingMessage = () => useChatStore(selectIsEditingMessage);

// Model Configuration Hooks
export const useDefaultModelConfig = () => useChatStore(selectDefaultModelConfig);
export const useCurrentSessionModelConfig = () => useChatStore(selectCurrentSessionModelConfig);

// Input Hooks
export const useInputMessage = () => useChatStore(selectInputMessage);
export const useHasInput = () => useChatStore(selectHasInput);
export const useCanSendMessage = () => useChatStore(selectCanSendMessage);

// Error Hooks
export const useChatError = () => useChatStore(selectError);
export const useHasError = () => useChatStore(selectHasError);

// Statistics Hooks
export const useTotalTokensUsed = () => useChatStore(selectTotalTokensUsed);
export const useTotalCost = () => useChatStore(selectTotalCost);
export const useSessionTokensUsed = () => useChatStore(selectSessionTokensUsed);
export const useSessionCost = () => useChatStore(selectSessionCost);
export const useAverageResponseTime = () => useChatStore(selectAverageResponseTime);

// Action Hooks
export const useChatActions = () => {
  const store = useChatStore();
  
  return {
    // Session Management
    createSession: store.createSession,
    deleteSession: store.deleteSession,
    setCurrentSession: store.setCurrentSession,
    updateSessionTitle: store.updateSessionTitle,
    clearAllSessions: store.clearAllSessions,
    
    // Message Operations
    sendMessage: store.sendMessage,
    addMessage: store.addMessage,
    updateMessage: store.updateMessage,
    deleteMessage: store.deleteMessage,
    regenerateMessage: store.regenerateMessage,
    clearMessages: store.clearMessages,
    
    // Message Editing
    startEditingMessage: store.startEditingMessage,
    cancelEditingMessage: store.cancelEditingMessage,
    saveEditedMessage: store.saveEditedMessage,
    setEditingContent: store.setEditingContent,
    
    // Streaming
    startStreaming: store.startStreaming,
    updateStreamingContent: store.updateStreamingContent,
    stopStreaming: store.stopStreaming,
    
    // Model Configuration
    setDefaultModelConfig: store.setDefaultModelConfig,
    updateSessionModelConfig: store.updateSessionModelConfig,
    
    // System Prompts
    updateSessionSystemPrompt: store.updateSessionSystemPrompt,
    
    // Input Management
    setInputMessage: store.setInputMessage,
    clearInput: store.clearInput,
    
    // Error Handling
    setError: store.setError,
    clearError: store.clearError,
    
    // Statistics
    updateStatistics: store.updateStatistics,
    
    // Utility
    exportSession: store.exportSession,
    importSession: store.importSession,
    
    // Reset
    reset: store.reset,
  };
};

// Convenience hook that returns commonly used state and actions
export const useChatStoreState = () => {
  const sessions = useSessions();
  const currentSession = useCurrentSession();
  const messages = useMessages();
  const isLoading = useIsLoading();
  const isSending = useIsSending();
  const isRegenerating = useIsRegenerating();
  const isProcessing = useIsProcessing();
  const isStreaming = useIsStreaming();
  const error = useChatError();
  const inputMessage = useInputMessage();
  const canSendMessage = useCanSendMessage();
  const totalTokensUsed = useTotalTokensUsed();
  const totalCost = useTotalCost();
  const actions = useChatActions();
  
  return {
    // Sessions
    sessions,
    currentSession,
    
    // Messages
    messages,
    
    // Loading States
    isLoading,
    isSending,
    isRegenerating,
    isProcessing,
    isStreaming,
    
    // Error
    error,
    
    // Input
    inputMessage,
    canSendMessage,
    
    // Statistics
    totalTokensUsed,
    totalCost,
    
    // Actions
    ...actions,
  };
};

// Hook for chat input component
export const useChatInput = () => {
  const inputMessage = useInputMessage();
  const canSendMessage = useCanSendMessage();
  const isSending = useIsSending();
  const { setInputMessage, sendMessage, clearInput } = useChatActions();
  
  return {
    inputMessage,
    canSendMessage,
    isSending,
    setInputMessage,
    sendMessage,
    clearInput,
  };
};

// Hook for session management UI
export const useSessionManagement = () => {
  const sessions = useSessions();
  const currentSessionId = useCurrentSessionId();
  const sessionCount = useSessionCount();
  const { 
    createSession, 
    deleteSession, 
    setCurrentSession,
    updateSessionTitle,
    clearAllSessions 
  } = useChatActions();
  
  return {
    sessions,
    currentSessionId,
    sessionCount,
    createSession,
    deleteSession,
    setCurrentSession,
    updateSessionTitle,
    clearAllSessions,
  };
};

// Hook for message editing
export const useMessageEditing = () => {
  const editingMessageId = useEditingMessageId();
  const editingContent = useEditingContent();
  const isEditingMessage = useIsEditingMessage();
  const {
    startEditingMessage,
    cancelEditingMessage,
    saveEditedMessage,
    setEditingContent,
  } = useChatActions();
  
  return {
    editingMessageId,
    editingContent,
    isEditingMessage,
    startEditingMessage,
    cancelEditingMessage,
    saveEditedMessage,
    setEditingContent,
  };
};