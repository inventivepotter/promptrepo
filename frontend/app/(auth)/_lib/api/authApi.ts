import httpClient from '@/lib/httpClient';
import type { LoginResponse } from '../../_types/AuthState';
import type { User } from "../../../../types/User";
import type { ApiResult } from '@/types/ApiResponse';

export const authApi = {
  // Start OAuth flow - redirects to GitHub
  initiateLogin: async (): Promise<ApiResult<{ authUrl: string }>> => {
    return await httpClient.get<{ authUrl: string }>('/api/v0/auth/login/github');
  },

  // Exchange OAuth code for session token (called by backend after GitHub redirect)
  exchangeCodeForToken: async (code: string, state: string): Promise<ApiResult<LoginResponse>> => {
    return await httpClient.get<LoginResponse>(`/api/v0/auth/callback/github?code=${code}&state=${state}`);
  },

  // Verify current session and get user info (use explicit token for verification)
  verifySession: async (): Promise<ApiResult<User>> => {
    return await httpClient.get<User>('/api/v0/auth/verify');
  },

  // Logout and invalidate session (auto-auth will handle token)
  logout: async (): Promise<ApiResult<void>> => {
    return await httpClient.post<void>('/api/v0/auth/logout');
  },

  // Refresh session token (auto-auth will handle token)
  refreshSession: async (): Promise<ApiResult<{ sessionToken: string; expiresAt: string }>> => {
    return await httpClient.post<{ sessionToken: string; expiresAt: string }>('/api/v0/auth/refresh');
  }
};

export default authApi;