import httpClient from '@/lib/httpClient';
import { getAuthHeaders } from '@/utils/authHeaders';
import type { ApiResult } from '@/types/ApiResponse';
import type { OpenAIMessage } from '../../_types/ChatState';

export const chatApi = {
  // Chat completion endpoint
  chatCompletion: async (messages: OpenAIMessage[], promptId?: string): Promise<ApiResult<OpenAIMessage>> => {
    return await httpClient.post<OpenAIMessage>('/api/v0/chat/completions', {
      messages,
      prompt_id: promptId
    }, {
      headers: getAuthHeaders()
    });
  }
};

export default chatApi;