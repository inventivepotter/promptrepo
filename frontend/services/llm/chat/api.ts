import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

// Extract types from generated API schema
export type ChatCompletionRequest = components['schemas']['ChatCompletionRequest'];
type ChatCompletionResponse = components['schemas']['ChatCompletionResponse'];
export type ChatMessage = components['schemas']['ChatMessage'];

/**
 * Chat API client
 * All methods return OpenAPI-formatted responses
 */
export class ChatApi {
  /**
   * Send chat completion request
   * @param request - The chat completion request object
   * @returns OpenAPI response with chat completion data
   */
  static async chatCompletion(
    request: ChatCompletionRequest
  ): Promise<OpenApiResponse<ChatCompletionResponse>> {
    return await httpClient.post<ChatCompletionResponse>('/api/v0/llm/completions', request);
  }
}