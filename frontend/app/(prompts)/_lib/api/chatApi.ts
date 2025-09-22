import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

// Extract types from generated API schema
type ChatCompletionRequest = components['schemas']['ChatCompletionRequest'];
type ChatCompletionResponse = components['schemas']['ChatCompletionResponse'];
type ChatMessage = components['schemas']['ChatMessage'];

// Options interface for easier API usage
export interface ChatCompletionOptions {
  provider: string;
  model: string;
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stop?: string[];
  stream?: boolean;
}

export const chatApi = {
  // Chat completion endpoint
  chatCompletion: async (
    messages: ChatMessage[],
    options: ChatCompletionOptions,
    promptId?: string
  ): Promise<OpenApiResponse<ChatCompletionResponse>> => {
    const request: ChatCompletionRequest = {
      messages,
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
    
    return await httpClient.post<ChatCompletionResponse>('/api/v0/llm/completions', request);
  }
};

export default chatApi;