import type { ChatMessage, Tool } from '@/app/prompts/_types/ChatState';
import type { components } from '@/types/generated/api';

type PromptMeta = components['schemas']['PromptMeta'];

// Model configuration for chat sessions
export interface ModelConfig {
  provider: string;
  model: string;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
}

// Chat session type - represents a conversation
export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
  modelConfig: ModelConfig;
  systemPrompt?: string;
  promptId?: string; // Link to a prompt template if used
}

// Streaming state for real-time message updates
export interface StreamingState {
  isStreaming: boolean;
  streamingMessageId: string | null;
  streamingContent: string;
}

// Chat state interface
export interface ChatState {
  // Sessions
  sessions: ChatSession[];
  currentSessionId: string | null;
  
  // Messages (current session's messages for quick access)
  messages: ChatMessage[];
  
  // UI States
  isLoading: boolean;
  isSending: boolean;
  isRegenerating: boolean;
  isDeleting: boolean;
  error: string | null;
  
  // Streaming
  streaming: StreamingState;
  
  // Message editing
  editingMessageId: string | null;
  editingContent: string;
  
  // Model configuration (default for new sessions)
  defaultModelConfig: ModelConfig;
  
  // Input state
  inputMessage: string;
  
  // Template variables for prompt templates
  templateVariables: Record<string, string>;
  
  // Tools
  availableTools: Tool[];
  selectedTools: string[];
  
  // Statistics
  totalTokensUsed: number;
  totalCost: number;
}

// Chat actions interface
export interface ChatActions {
  // Session Management
  createSession: (title?: string, modelConfig?: ModelConfig, systemPrompt?: string) => ChatSession;
  deleteSession: (sessionId: string) => void;
  setCurrentSession: (sessionId: string | null) => void;
  updateSessionTitle: (sessionId: string, title: string) => void;
  clearAllSessions: () => void;
  
  // Message Operations
  sendMessage: (
    content: string,
    options?: {
      promptMeta: PromptMeta;
      onStream?: (chunk: string) => void;
    }
  ) => Promise<void>;
  
  addMessage: (message: ChatMessage) => void;
  updateMessage: (messageId: string, updates: Partial<ChatMessage>) => void;
  deleteMessage: (messageId: string) => void;
  regenerateMessage: (messageId: string) => Promise<void>;
  clearMessages: () => void;
  
  // Message Editing
  startEditingMessage: (messageId: string) => void;
  cancelEditingMessage: () => void;
  saveEditedMessage: () => Promise<void>;
  setEditingContent: (content: string) => void;
  
  // Streaming
  startStreaming: (messageId: string) => void;
  updateStreamingContent: (content: string) => void;
  stopStreaming: () => void;
  
  // Model Configuration
  setDefaultModelConfig: (config: Partial<ModelConfig>) => void;
  updateSessionModelConfig: (sessionId: string, config: Partial<ModelConfig>) => void;
  
  // System Prompts
  updateSessionSystemPrompt: (sessionId: string, systemPrompt: string) => void;
  
  // Input Management
  setInputMessage: (message: string) => void;
  clearInput: () => void;
  
  // Template Variables Management
  setTemplateVariable: (name: string, value: string) => void;
  clearTemplateVariables: () => void;
  
  // Tools Management
  setAvailableTools: (tools: Tool[]) => void;
  setSelectedTools: (toolIds: string[]) => void;
  toggleTool: (toolId: string) => void;
  clearSelectedTools: () => void;
  
  // Error Handling
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // Statistics
  updateStatistics: (tokensUsed: number, cost: number) => void;
  
  // Utility
  exportSession: (sessionId: string) => ChatSession | null;
  importSession: (session: ChatSession) => void;
  
  // Reset
  reset: () => void;
}

export interface ChatStore extends ChatState, ChatActions {}