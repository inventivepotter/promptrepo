import { errorNotification } from '@/lib/notifications';
import { pricingService } from '@/services/llm/pricing/pricingService';
import { ChatApi, type ChatCompletionRequest, type ChatMessage as ApiChatMessage } from './api';
import type { OpenAIMessage, ChatMessage } from '@/app/(prompts)/_types/ChatState';
import type { ChatCompletionOptions, TokenUsage, UsageWithReasoning } from '@/types/Chat';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { TokenUsage as PricingTokenUsage } from '@/types/Pricing';


/**
 * Chat service that handles all chat-related operations.
 * This includes sending messages, processing responses, and handling errors.
 * Following single responsibility principle - only handles chat concerns.
 */
export class ChatService {
  /**
   * Send messages to chat completion endpoint and get AI response.
   * Handles error notifications and fallback behavior.
   * @param messages - Array of OpenAI formatted messages
   * @param promptId - Optional prompt ID
   * @param options - Chat completion options
   * @param systemMessage - Optional system message to prepend
   * @returns The assistant's message or null if an error occurs
   */
  async sendChatCompletion(
    messages: OpenAIMessage[],
    promptId?: string,
    options?: ChatCompletionOptions,
    systemMessage?: string
  ): Promise<ChatMessage | null> {
    try {
      // Validate completion options
      if (!options?.provider || !options.provider.trim()) {
        errorNotification(
          'Missing Provider',
          'Please select a provider (e.g., openai, anthropic) in the prompt editor before sending a message.'
        );
        return null;
      }

      if (!options?.model || !options.model.trim()) {
        errorNotification(
          'Missing Model',
          'Please select a model (e.g., gpt-4, claude-3) in the prompt editor before sending a message.'
        );
        return null;
      }

      // Use provided system message or ensure first message is a system message
      let messagesWithSystem: OpenAIMessage[];

      if (systemMessage) {
        // If a system message is provided, use it
        const systemMsg: OpenAIMessage = {
          role: 'system' as const,
          content: systemMessage
        };

        // Remove any existing system message and prepend the new one
        const nonSystemMessages = messages.filter(msg => msg.role !== 'system');
        messagesWithSystem = [systemMsg, ...nonSystemMessages];
      } else {
        // No system message provided - this should result in an error from backend
        messagesWithSystem = messages;
      }

      const request: ChatCompletionRequest = {
        messages: messagesWithSystem as ApiChatMessage[],
        provider: options.provider,
        model: options.model,
        prompt_id: promptId || null,
        stream: options.stream || false,
        temperature: options.temperature || null,
        max_tokens: options.max_tokens || null,
        top_p: options.top_p || null,
        frequency_penalty: options.frequency_penalty || null,
        presence_penalty: options.presence_penalty || null,
        stop: options.stop || null
      };

      const result = await ChatApi.chatCompletion(request);

      if (isErrorResponse(result)) {
        // Show user-friendly notification
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

      // Extract the assistant message from the completion response
      if (!result.data.choices || result.data.choices.length === 0) {
        errorNotification(
          'Invalid Response',
          'The AI service returned an invalid response format.'
        );
        return null;
      }

      const assistantMessage = result.data.choices[0].message as OpenAIMessage & {
        tool_call_id?: string | null;
        tool_calls?: OpenAIMessage['tool_calls'] | null;
      };

      // Pre-process the usage object to handle null values
      const usage = result.data.usage ? {
        prompt_tokens: result.data.usage.prompt_tokens ?? undefined,
        completion_tokens: result.data.usage.completion_tokens ?? undefined,
        total_tokens: result.data.usage.total_tokens ?? undefined,
        reasoning_tokens: (result.data.usage as UsageWithReasoning).reasoning_tokens ?? undefined
      } : undefined;

      // Convert response back to internal ChatMessage format
      const chatMessage = this.fromOpenAIMessage(assistantMessage, `assistant-${Date.now()}`, usage, options.model);

      // Add inference time from API response
      if (result.data.inference_time_ms) {
        chatMessage.inferenceTimeMs = result.data.inference_time_ms;
      }

      return chatMessage;
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
   * Convert OpenAI message to internal ChatMessage format
   */
  public fromOpenAIMessage(
    openAIMessage: OpenAIMessage,
    id?: string,
    usage?: { prompt_tokens?: number; completion_tokens?: number; total_tokens?: number; reasoning_tokens?: number },
    model?: string
  ): ChatMessage {
    // Handle potential null values for tool_call_id and tool_calls to match OpenAIMessage type
    const processedMessage: OpenAIMessage = {
      ...openAIMessage,
      tool_call_id: openAIMessage.tool_call_id === null ? undefined : openAIMessage.tool_call_id,
      tool_calls: openAIMessage.tool_calls === null ? undefined : openAIMessage.tool_calls
    };

    const message: ChatMessage = {
      id: id || `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      usage: usage ? {
        prompt_tokens: usage.prompt_tokens ?? undefined,
        completion_tokens: usage.completion_tokens ?? undefined,
        total_tokens: usage.total_tokens ?? undefined,
        reasoning_tokens: usage.reasoning_tokens ?? undefined
      } : undefined,
      model,
      ...processedMessage
    };

    // Calculate cost if usage and model are provided
    if (usage && model && processedMessage.role === 'assistant') {
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

  /**
   * Extract token usage from ChatMessage for pricing calculations
   */
  public getTokenUsageFromMessage(message: ChatMessage): PricingTokenUsage | null {
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
  public async calculateMessageCost(message: ChatMessage): Promise<number | null> {
    if (!message.model || !message.usage) return null;
    
    const tokenUsage = this.getTokenUsageFromMessage(message);
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
}

// Export singleton instance
export const chatService = new ChatService();

// Export class for testing or custom instances
export default chatService;