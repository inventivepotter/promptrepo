/**
 * API client for conversational services
 *
 * Handles HTTP requests for conversation simulation.
 */

import httpClient from '@/lib/httpClient';
import type { StandardResponse, StandardErrorResponse } from '@/types/OpenApiResponse';
import type {
  SimulateConversationRequest,
  SimulateConversationResponse,
} from '@/types/eval';

const BASE_URL = '/api/v0/conversational';

/**
 * API client for conversational endpoints
 */
const ConversationalApi = {
  /**
   * Simulate a conversation based on user goal
   * @param request - Simulation request
   * @returns Simulated conversation or error
   */
  async simulateConversation(
    request: SimulateConversationRequest
  ): Promise<StandardResponse<SimulateConversationResponse> | StandardErrorResponse> {
    const response = await httpClient.post<SimulateConversationResponse>(`${BASE_URL}/simulate`, request);
    return response as StandardResponse<SimulateConversationResponse> | StandardErrorResponse;
  },
};

export default ConversationalApi;
