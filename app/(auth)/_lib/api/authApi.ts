import httpClient from '@/lib/httpClient';
import type { LoginResponse, User } from '../../_types/AuthState';
import type { ApiResult } from '@/types/ApiResponse';

export const authApi = {
  // Start OAuth flow - redirects to GitHub
  initiateLogin: async (): Promise<ApiResult<{ authUrl: string }>> => {
    return await httpClient.get<{ authUrl: string }>('/v0/auth/login/github');
  },

  // Exchange OAuth code for session token (called by backend after GitHub redirect)
  exchangeCodeForToken: async (code: string, state: string): Promise<ApiResult<LoginResponse>> => {
    return await httpClient.post<LoginResponse>('/v0/auth/callback/github', { code, state });
  },

  // Verify current session and get user info
  verifySession: async (sessionToken: string): Promise<ApiResult<User>> => {
    return await httpClient.get<User>('/v0/auth/verify', {
      headers: { 'Authorization': `Bearer ${sessionToken}` }
    });
  },

  // Logout and invalidate session
  logout: async (sessionToken: string): Promise<ApiResult<void>> => {
    return await httpClient.post<void>('/v0/auth/logout', {}, {
      headers: { 'Authorization': `Bearer ${sessionToken}` }
    });
  },

  // Refresh session token
  refreshSession: async (sessionToken: string): Promise<ApiResult<{ sessionToken: string; expiresAt: string }>> => {
    return await httpClient.post<{ sessionToken: string; expiresAt: string }>('/v0/auth/refresh', {}, {
      headers: { 'Authorization': `Bearer ${sessionToken}` }
    });
  }
};

export default authApi;