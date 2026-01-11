/**
 * Types for shared chat functionality.
 */

export interface SharedChatTokenUsage {
  prompt_tokens?: number;
  completion_tokens?: number;
  total_tokens?: number;
  reasoning_tokens?: number;
}

export interface SharedChatToolCall {
  id: string;
  name: string;
  arguments: Record<string, unknown>;
}

export interface SharedChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system' | 'tool';
  content: string;
  timestamp: string;
  usage?: SharedChatTokenUsage;
  cost?: number;
  inference_time_ms?: number;
  tool_calls?: SharedChatToolCall[];
}

export interface SharedChatModelConfig {
  provider: string;
  model: string;
  temperature?: number;
  max_tokens?: number;
}

export interface CreateSharedChatRequest {
  title: string;
  messages: SharedChatMessage[];
  model_config_data: SharedChatModelConfig;
  prompt_meta?: Record<string, unknown>;
  total_tokens: number;
  total_cost: number;
}

export interface SharedChatResponse {
  id: string;
  share_id: string;
  title: string;
  messages: SharedChatMessage[];
  model_config_data: SharedChatModelConfig;
  prompt_meta?: Record<string, unknown>;
  total_tokens: number;
  total_cost: number;
  created_at: string;
}

export interface CreateSharedChatResponse {
  share_id: string;
  share_url: string;
}

export interface SharedChatListItem {
  id: string;
  share_id: string;
  title: string;
  total_tokens: number;
  total_cost: number;
  created_at: string;
  message_count: number;
}
