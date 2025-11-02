import { errorNotification } from '@/lib/notifications';
import { ChatApi, type ChatCompletionRequest } from './api';
import type { OpenAIMessage, ChatMessage } from '@/app/prompts/_types/ChatState';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

type PromptMeta = components['schemas']['PromptMeta'];
type MessageSchema = components['schemas']['UserMessageSchema'] | components['schemas']['AIMessageSchema'] | components['schemas']['SystemMessageSchema'] | components['schemas']['ToolMessageSchema'];


/**
 * Chat service that handles all chat-related operations.
 * This includes sending messages, processing responses, and handling errors.
 * Following single responsibility principle - only handles chat concerns.
 */
export class ChatService {
  /**
   * Send chat completion request using PromptMeta.
   * @param promptMeta - The prompt metadata containing full configuration
   * @param messages - Optional conversation history
   * @returns The assistant's message or null if an error occurs
   */
  async sendChatCompletion(
    promptMeta: PromptMeta,
    messages?: MessageSchema[]
  ): Promise<{ message: ChatMessage; toolCalls?: MessageSchema[] } | null> {
    try {
      // Validate prompt_meta
      if (!promptMeta?.prompt?.provider || !promptMeta.prompt.provider.trim()) {
        errorNotification(
          'Missing Provider',
          'Please select a provider (e.g., openai, anthropic) in the prompt editor before sending a message.'
        );
        return null;
      }

      if (!promptMeta?.prompt?.model || !promptMeta.prompt.model.trim()) {
        errorNotification(
          'Missing Model',
          'Please select a model (e.g., gpt-4, claude-3) in the prompt editor before sending a message.'
        );
        return null;
      }

      const request: ChatCompletionRequest = {
        prompt_meta: promptMeta,
        messages: messages || null
      };

      const result = await ChatApi.chatCompletion(request);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Chat Request Failed',
          result.detail || 'Unable to get response from AI service. Please try again.'
        );
        return null;
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'No Response',
          'The AI service did not return a response. Please try again.'
        );
        return null;
      }

      const responseData = result.data;

      // Extract usage and cost from backend response
      const usage = responseData.usage ? {
        prompt_tokens: responseData.usage.input_tokens,
        completion_tokens: responseData.usage.output_tokens,
        total_tokens: responseData.usage.total_tokens,
      } : undefined;

      // Create chat message from response
      const chatMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: responseData.content,
        timestamp: new Date(),
        usage,
        cost: responseData.cost?.total_cost,
        inferenceTimeMs: responseData.duration_ms ?? undefined,
      };


      // Return both the message and tool calls
      return {
        message: chatMessage,
        toolCalls: responseData.tool_calls || undefined
      };
    } catch (error: unknown) {
      console.error('Error in chat completion:', error);
      errorNotification(
        'Connection Error',
        'Unable to connect to chat service. Please check your connection and try again.'
      );
      return null;
    }
  }

  /**
   * Convert internal ChatMessage to OpenAI format for API calls
   */
  public toOpenAIMessage(message: ChatMessage): OpenAIMessage {
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
  public toOpenAIMessages(messages: ChatMessage[]): OpenAIMessage[] {
    return messages.map(msg => this.toOpenAIMessage(msg));
  }

  /**
   * Convert OpenAI message to internal ChatMessage format (simplified - cost now from backend)
   */
  public fromOpenAIMessage(
    openAIMessage: OpenAIMessage,
    id?: string,
    usage?: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number; reasoning_tokens?: number }
  ): ChatMessage {
    // Handle potential null values for tool_call_id and tool_calls to match OpenAIMessage type
    const processedMessage: OpenAIMessage = {
      ...openAIMessage,
      tool_call_id: openAIMessage.tool_call_id === null ? undefined : openAIMessage.tool_call_id,
      tool_calls: openAIMessage.tool_calls === null ? undefined : openAIMessage.tool_calls
    };

    return {
      id: id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      usage: usage ? {
        prompt_tokens: usage.prompt_tokens ?? undefined,
        completion_tokens: usage.completion_tokens ?? undefined,
        total_tokens: usage.total_tokens ?? undefined,
        reasoning_tokens: usage.reasoning_tokens ?? undefined
      } : undefined,
      ...processedMessage
    };
  }

  /**
   * Create a message in the correct format for any role
   */
  public createMessage(
    role: ChatMessage['role'],
    content: string,
    options?: {
      tool_calls?: OpenAIMessage['tool_calls'];
      tool_call_id?: string;
    }
  ): ChatMessage {
    return {
      id: `${role}-${Date.now()}`,
      role,
      content,
      timestamp: new Date(),
      ...options
    };
  }

  // Convenience methods using the unified createMessage
  public createUserMessage = (content: string) => this.createMessage('user', content);
  public createAssistantMessage = (content: string, tool_calls?: OpenAIMessage['tool_calls']) =>
    this.createMessage('assistant', content, { tool_calls });
  public createSystemMessage = (content: string) => this.createMessage('system', content);
  public createToolMessage = (content: string, tool_call_id: string) =>
    this.createMessage('tool', content, { tool_call_id });

}

// Export singleton instance
export const chatService = new ChatService();

// Export class for testing or custom instances
export default chatService;