import { ChatMessage, OpenAIMessage } from '../../_types/ChatState';

/**
 * Convert internal ChatMessage to OpenAI format for API calls
 */
export function toOpenAIMessage(message: ChatMessage): OpenAIMessage {
  return {
    role: message.role,
    content: message.content,
    tool_call_id: message.tool_call_id,
    tool_calls: message.tool_calls
  };
}

/**
 * Convert array of internal ChatMessages to OpenAI format for API calls
 */
export function toOpenAIMessages(messages: ChatMessage[]): OpenAIMessage[] {
  return messages.map(toOpenAIMessage);
}

/**
 * Convert OpenAI message to internal ChatMessage format
 */
export function fromOpenAIMessage(openAIMessage: OpenAIMessage, id?: string): ChatMessage {
  return {
    id: id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date(),
    ...openAIMessage
  };
}

/**
 * Create a user message in the correct format
 */
export function createUserMessage(content: string): ChatMessage {
  return {
    id: `user-${Date.now()}`,
    role: 'user',
    content,
    timestamp: new Date(),
  };
}

/**
 * Create an assistant message in the correct format
 */
export function createAssistantMessage(content: string, tool_calls?: OpenAIMessage['tool_calls']): ChatMessage {
  return {
    id: `assistant-${Date.now()}`,
    role: 'assistant',
    content,
    timestamp: new Date(),
    tool_calls
  };
}

/**
 * Create a system message in the correct format
 */
export function createSystemMessage(content: string): ChatMessage {
  return {
    id: `system-${Date.now()}`,
    role: 'system',
    content,
    timestamp: new Date(),
  };
}

/**
 * Create a tool message in the correct format
 */
export function createToolMessage(content: string, tool_call_id: string): ChatMessage {
  return {
    id: `tool-${Date.now()}`,
    role: 'tool',
    content,
    tool_call_id,
    timestamp: new Date(),
  };
}