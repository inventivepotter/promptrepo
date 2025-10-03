// Main store
export { useChatStore } from './store';

// Types
export type {
  ChatState,
  ChatActions,
  ChatStore,
  ChatSession,
  StreamingState,
  ModelConfig,
} from './types';

// Selectors
export {
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

// Hooks
export {
  // Session Hooks
  useSessions,
  useCurrentSessionId,
  useCurrentSession,
  useSessionById,
  useSessionCount,
  useHasSessions,
  useRecentSessions,
  useSessionsByDateRange,
  useSessionSummary,
  useSessionsWithStats,
  useIsSessionActive,
  
  // Message Hooks
  useMessages,
  useLastMessage,
  useUserMessages,
  useAssistantMessages,
  useMessageById,
  useMessageCount,
  useHasMessages,
  useMessagesWithTokenUsage,
  useCanRegenerateLastMessage,
  
  // Loading State Hooks
  useIsLoading,
  useIsSending,
  useIsRegenerating,
  useIsDeleting,
  useIsProcessing,
  
  // Streaming Hooks
  useIsStreaming,
  useStreamingMessageId,
  useStreamingContent,
  
  // Editing Hooks
  useEditingMessageId,
  useEditingContent,
  useIsEditingMessage,
  
  // Model Configuration Hooks
  useDefaultModelConfig,
  useCurrentSessionModelConfig,
  
  // Input Hooks
  useInputMessage,
  useHasInput,
  useCanSendMessage,
  
  // Error Hooks
  useChatError,
  useHasError,
  
  // Statistics Hooks
  useTotalTokensUsed,
  useTotalCost,
  useSessionTokensUsed,
  useSessionCost,
  useAverageResponseTime,
  
  // Action Hooks
  useChatActions,
  
  // Convenience Hooks
  useChatStoreState,
  useChatInput,
  useSessionManagement,
  useMessageEditing,
} from './hooks';