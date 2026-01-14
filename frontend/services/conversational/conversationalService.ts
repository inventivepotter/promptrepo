/**
 * Conversational Service
 *
 * Provides methods for simulating multi-turn conversations
 * with proper error handling and notifications.
 */

import ConversationalApi from './api';
import { errorNotification } from '@/lib/notifications';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type {
  SimulateConversationRequest,
  SimulateConversationResponse,
} from '@/types/eval';

/**
 * Service for conversational test simulation
 */
export class ConversationalService {
  /**
   * Simulate a conversation based on user goal
   *
   * @param request - Simulation request
   * @returns Simulated conversation
   */
  static async simulateConversation(
    request: SimulateConversationRequest
  ): Promise<SimulateConversationResponse> {
    try {
      const result = await ConversationalApi.simulateConversation(request);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Conversation Simulation Failed',
          result.detail || 'Unable to simulate conversation.'
        );
        throw new Error(result.detail || 'Failed to simulate conversation');
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        throw new Error('Unexpected response format');
      }

      return result.data;
    } catch (error: unknown) {
      if (error instanceof Error && !error.message.includes('Failed to simulate')) {
        errorNotification(
          'Connection Error',
          'Unable to connect to conversation simulation service.'
        );
      }
      throw error;
    }
  }
}
