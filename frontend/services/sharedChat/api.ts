/**
 * Shared Chat API client.
 */
import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type {
  CreateSharedChatRequest,
  CreateSharedChatResponse,
  SharedChatResponse,
  SharedChatListItem,
} from './types';

/**
 * Shared Chat API client
 * Handles all shared chat API operations.
 */
export class SharedChatApi {
  /**
   * Create a new shared chat.
   * @param request - The create shared chat request
   * @returns OpenAPI response with share ID and URL
   */
  static async createSharedChat(
    request: CreateSharedChatRequest
  ): Promise<OpenApiResponse<CreateSharedChatResponse>> {
    return await httpClient.post<CreateSharedChatResponse>(
      '/api/v0/shared-chats',
      request
    );
  }

  /**
   * Get a shared chat by its share ID.
   * @param shareId - The share identifier
   * @returns OpenAPI response with shared chat data
   */
  static async getSharedChat(
    shareId: string
  ): Promise<OpenApiResponse<SharedChatResponse>> {
    return await httpClient.get<SharedChatResponse>(
      `/api/v0/shared-chats/${shareId}`
    );
  }

  /**
   * List all shared chats for the current user.
   * @param limit - Maximum number of results (default 50)
   * @param offset - Pagination offset (default 0)
   * @returns OpenAPI response with list of shared chats
   */
  static async listSharedChats(
    limit: number = 50,
    offset: number = 0
  ): Promise<OpenApiResponse<SharedChatListItem[]>> {
    return await httpClient.get<SharedChatListItem[]>(
      `/api/v0/shared-chats?limit=${limit}&offset=${offset}`
    );
  }

  /**
   * Delete a shared chat.
   * @param shareId - The share identifier
   * @returns OpenAPI response with success boolean
   */
  static async deleteSharedChat(
    shareId: string
  ): Promise<OpenApiResponse<boolean>> {
    return await httpClient.delete<boolean>(
      `/api/v0/shared-chats/${shareId}`
    );
  }
}
