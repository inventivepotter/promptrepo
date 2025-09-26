import httpClient from '@/lib/httpClient';
import type { OpenApiResponse } from '@/types/OpenApiResponse';
import type { components } from '@/types/generated/api';

// Extract types from generated API schema
type AuthUrlResponseData = components['schemas']['AuthUrlResponseData'];
type LoginResponseData = components['schemas']['LoginResponseData'];
type User = components['schemas']['User'];

export const authApi = {
  // Start OAuth flow - redirects to GitHub
  initiateLogin: async (promptrepoRedirectUrl?: string): Promise<OpenApiResponse<AuthUrlResponseData>> => {
    const params = new URLSearchParams();
    if (promptrepoRedirectUrl) {
      params.append('promptrepo_redirect_url', promptrepoRedirectUrl);
    }
    const queryString = params.toString();
    return await httpClient.get<AuthUrlResponseData>(`/api/v0/auth/login/github/${queryString ? `?${queryString}` : ''}`);
  },

  // Exchange OAuth code for session token (called by backend after GitHub redirect)
  handleGithubCallback: async (code: string, state: string): Promise<OpenApiResponse<LoginResponseData>> => {
    const params = new URLSearchParams({
      code,
      state
    });
    return await httpClient.get<LoginResponseData>(`/api/v0/auth/callback/github/?${params.toString()}`);
  },

  // Verify current session and get user info
  verifySession: async (): Promise<OpenApiResponse<User>> => {
    return await httpClient.get<User>('/api/v0/auth/verify');
  },

  // Logout and invalidate session
  logout: async (): Promise<OpenApiResponse<Record<string, unknown>>> => {
    return await httpClient.post<Record<string, unknown>>('/api/v0/auth/logout');
  },

  // Refresh session token
  refreshSession: async (): Promise<OpenApiResponse<null>> => {
    return await httpClient.post<null>('/api/v0/auth/refresh');
  }
};

export default authApi;