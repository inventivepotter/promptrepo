import httpClient from '@/lib/httpClient';
import { getAuthHeaders } from '@/utils/authHeaders';
import type { ApiResult } from '@/types/ApiResponse';
import type { OpenAIMessage } from '../../_types/ChatState';
import type { ChatCompletionOptions, ChatCompletionResponse } from '../../_types/ChatApi';

export const chatApi = {
  // Chat completion endpoint
  chatCompletion: async (
    messages: OpenAIMessage[],
    promptId?: string,
    options?: ChatCompletionOptions
  ): Promise<ApiResult<ChatCompletionResponse>> => {
    return await httpClient.post<ChatCompletionResponse>('/api/v0/chat/completions', {
      messages,
      prompt_id: promptId,
      provider: options?.provider,
      model: options?.model,
      temperature: options?.temperature ?? 0.7,
      max_tokens: options?.max_tokens,
      top_p: options?.top_p,
      frequency_penalty: options?.frequency_penalty,
      presence_penalty: options?.presence_penalty,
      stop: options?.stop,
      stream: options?.stream ?? false
    }, {
      headers: getAuthHeaders()
    });
  }
};

export default chatApi;