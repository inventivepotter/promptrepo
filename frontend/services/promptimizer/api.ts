/**
 * Promptimizer API service.
 *
 * This service provides methods for interacting with the Promptimizer backend API.
 */
import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';

/**
 * Request model for prompt optimization.
 */
export interface PromptOptimizerRequest {
  idea: string;
  provider: string;
  model: string;
  expects_user_message: boolean;
  conversation_history?: Array<{
    role: string;
    content: string;
  }>;
  current_prompt?: string;
}

/**
 * Response model for prompt optimization.
 */
export interface PromptOptimizerResponse {
  optimized_prompt: string;
  explanation?: string | null;
}

/**
 * Promptimizer API client.
 */
export const promptOptimizerApi = {
  /**
   * Optimize a prompt based on user's idea and provider-specific best practices.
   *
   * @param request - The optimization request parameters
   * @returns Promise resolving to the optimized prompt response
   */
  optimize: async (
    request: PromptOptimizerRequest
  ): Promise<OpenApiResponse<PromptOptimizerResponse>> => {
    return await httpClient.post<PromptOptimizerResponse>(
      '/api/v0/promptimizer/optimize',
      request
    );
  },
};
