import type { OpenAIMessage, ChatMessage } from '../_types/ChatState';
import { chatApi } from './api/chatApi';
import { fromOpenAIMessage } from './utils/messageUtils';
import { errorNotification } from '@/lib/notifications';

/**
 * Send messages to chat completion endpoint and get AI response
 * Handles error notifications and fallback behavior
 */
export async function chatCompletion(messages: OpenAIMessage[], promptId?: string): Promise<ChatMessage | null> {
  try {
    const result = await chatApi.chatCompletion(messages, promptId);
    
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

    // Convert response back to internal ChatMessage format
    const chatMessage = fromOpenAIMessage(result.data, `assistant-${Date.now()}`);
    
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