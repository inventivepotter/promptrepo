import type { OpenAIMessage, ChatMessage } from '../_types/ChatState';
import type { ChatCompletionOptions } from '../_types/ChatApi';
import { chatApi } from './api/chatApi';
import { fromOpenAIMessage } from './utils/messageUtils';
import { errorNotification } from '@/lib/notifications';

/**
 * Send messages to chat completion endpoint and get AI response
 * Handles error notifications and fallback behavior
 */
export async function chatCompletion(
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

    const result = await chatApi.chatCompletion(messagesWithSystem, promptId, options);
    
    if (!result.success) {
      // Show user-friendly notification
      errorNotification(
        result.error || 'Chat Request Failed',
        result.message || 'Unable to get response from AI service. Please try again.'
      );
      return null;
    }

    if (!result.data) {
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

    const assistantMessage = result.data.choices[0].message;
    
    // Convert response back to internal ChatMessage format
    const chatMessage = fromOpenAIMessage(assistantMessage, `assistant-${Date.now()}`);
    
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