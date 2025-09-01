import { ChatMessage, OpenAIMessage } from '../../_types/ChatState';
import { pricingService } from './pricingUtils';
import { TokenUsage } from '../../_types/PricingTypes';

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
export function fromOpenAIMessage(
  openAIMessage: OpenAIMessage,
  id?: string,
  usage?: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number; reasoning_tokens?: number },
  model?: string
): ChatMessage {
  const message: ChatMessage = {
    id: id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date(),
    usage,
    model,
    ...openAIMessage
  };

  // Calculate cost if usage and model are provided
  if (usage && model && openAIMessage.role === 'assistant') {
    const tokenUsage: TokenUsage = {
      inputTokens: usage.prompt_tokens || 0,
      outputTokens: usage.completion_tokens || 0,
      reasoningTokens: usage.reasoning_tokens
    };
    
    const costCalculation = pricingService.calculateCost(model, tokenUsage);
    if (costCalculation) {
      message.cost = costCalculation.totalCost;
    }
  }

  return message;
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

/**
 * Extract token usage from ChatMessage for pricing calculations
 */
export function getTokenUsageFromMessage(message: ChatMessage): TokenUsage | null {
  if (!message.usage) return null;
  
  return {
    inputTokens: message.usage.prompt_tokens || 0,
    outputTokens: message.usage.completion_tokens || 0,
    reasoningTokens: message.usage.reasoning_tokens
  };
}

/**
 * Calculate cost for a message if model and usage are available
 */
export async function calculateMessageCost(message: ChatMessage): Promise<number | null> {
  if (!message.model || !message.usage) return null;
  
  const tokenUsage = getTokenUsageFromMessage(message);
  if (!tokenUsage) return null;
  
  try {
    await pricingService.getPricingData();
    const costCalculation = pricingService.calculateCost(message.model, tokenUsage);
    return costCalculation?.totalCost || null;
  } catch (error) {
    console.warn('Failed to calculate message cost:', error);
    return null;
  }
}