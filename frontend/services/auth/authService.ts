import * as authStore from '@/stores/authStore';
import { authApi } from './api';
import { errorNotification } from '@/lib/notifications';
import { LOCAL_STORAGE_KEYS } from '@/utils/localStorageConstants';
import type { components } from '@/types/generated/api';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { LoginResponse } from '@/app/(auth)/_types/AuthState';

type User = components['schemas']['User'];

/**
 * Authentication service that handles all authentication-related operations.
 * This includes session management, user data handling, and interactions with the auth API.
 * Following single responsibility principle - only handles auth concerns.
 */
export class AuthService {
  /**
   * Get authentication headers for API requests
   * @returns Headers object with Authorization header
   */
  getAuthHeaders(): Record<string, string> {
    const sessionToken = authStore.getSessionToken();
    if (!sessionToken) {
      return {
        'Authorization': ''
      };
    }
    return {
      'Authorization': `Bearer ${sessionToken}`
    };
  }

  /**
   * Get the raw session token
   * @returns Session token string or null if not authenticated
   */
  getSessionToken(): string | null {
    return authStore.getSessionToken();
  }

  /**
   * Check if user is authenticated
   * @returns true if user has a valid session token
   */
  isAuthenticated(): boolean {
    const token = authStore.getSessionToken();
    return Boolean(token && token.trim().length > 0);
  }

  /**
   * Set session token and user data (for login scenarios)
   * @param token - The session token to store
   * @param expiresAt - The expiration date string
   * @param user - The user data to store
   */
  setSession(token: string, expiresAt: string, user?: User): void {
    authStore.setSession(token, expiresAt);
    if (user) {
      authStore.setUserData(user);
    }
  }

  /**
   * Clear session token and user data (for logout scenarios)
   */
  clearSession(): void {
    authStore.clearSession();
    authStore.clearUserData();
  }

  /**
   * Get the authorization URL for initiating the OAuth flow.
   * @param promptrepoRedirectUrl - Optional PromptRepo app URL to redirect after login.
   * @returns The authorization URL or null if an error occurs.
   */
  async getAuthUrl(promptrepoRedirectUrl?: string): Promise<string | null> {
    try {
      const result = await authApi.initiateLogin(promptrepoRedirectUrl);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Login Failed',
          result.detail || 'Could not initiate GitHub login. Please try again.'
        );
        return null;
      }

      if (!isStandardResponse(result) || !result.data) {
         errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        return null;
      }

      return result.data.authUrl;

    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to connect to authentication service. Using mock URL in development.'
      );
      return null;
    }
  }

  /**
   * Get the currently authenticated user's data.
   * Verifies the session with the backend and refreshes local session.
   * @returns The user data or null if not authenticated or an error occurs.
   */
  async getUser(): Promise<User | null> {
    try {
      const currentSessionToken = authStore.getSessionToken();
      if (!currentSessionToken) {
        return null;
      }

      const result = await authApi.verifySession();

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Session Verification Failed',
          result.detail || 'Could not verify user session. Please log in again.'
        );
        this.clearSession();
        return null;
      }
      
      if (!isStandardResponse(result) || !result.data) {
         errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        this.clearSession();
        return null;
      }

      // Store verified user data and refresh session
      authStore.setUserData(result.data);
      
      // Re-store session with a new expiry time to keep it fresh
      const newExpiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(); // 24 hours
      authStore.setSession(currentSessionToken, newExpiresAt);
      
      return result.data;

    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to verify user session. Using cached data.'
      );
      return null;
    }
  }

  /**
   * Handles the authentication callback from the OAuth provider.
   * Exchanges the authorization code for a session token and stores the session.
   * @param code - The authorization code from the OAuth provider.
   * @param state - The state parameter from the OAuth provider.
   * @returns The login response data with optional promptrepoRedirectUrl or null if an error occurs.
   */
  async handleCallback(code: string, state: string): Promise<LoginResponse | null> {
    try {
      const result = await authApi.exchangeCodeForToken(code, state);

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Authentication Failed',
          result.detail || 'Could not complete GitHub authentication. Please try again.'
        );
        return null;
      }

      if (!isStandardResponse(result) || !result.data) {
         errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        return null;
      }

      // Store session and user data
      this.setSession(result.data.sessionToken, result.data.expiresAt, result.data.user);
      
      // Return the full response including optional promptrepoRedirectUrl
      return result.data;

    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to complete authentication. Using mock data in development.'
      );
      return null;
    }
  }

  /**
   * Logs out the current user by invalidating the session on the server and clearing local data.
   * @returns true if the logout was successful (client-side), false otherwise.
   */
  async logout(): Promise<boolean> {
    try {
      const sessionToken = authStore.getSessionToken();
      
      if (sessionToken) {
        // Attempt to invalidate session on server
        const result = await authApi.logout();

        if (isErrorResponse(result)) {
          errorNotification(
            result.title || 'Logout Error',
            result.detail || 'Could not complete logout on server. Clearing local session.'
          );
        }
      }
      
      // Always clear all local data regardless of server response
      this.clearAllUserData();
      
      return true;

    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to complete server logout. Clearing local session.'
      );
      
      // Clear all local data even if server request fails
      this.clearAllUserData();
      
      return true;
    }
  }

  /**
   * Refreshes the current session token and user data.
   * @returns An object indicating success and the user data if successful.
   */
  async refreshSession(): Promise<{ success: boolean; user: User | null }> {
    try {
      const sessionToken = authStore.getSessionToken();
      if (!sessionToken) {
        return { success: false, user: null };
      }

      // Only refresh if needed
      if (!authStore.shouldRefreshSession()) {
        const cachedUser = authStore.getUserData();
        return { success: true, user: cachedUser };
      }

      const result = await authApi.refreshSession();

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Session Refresh Failed',
          result.detail || 'Could not refresh your session. Please log in again.'
        );
        this.clearSession();
        return { success: false, user: null };
      }

      if (!isStandardResponse(result) || !result.data) {
         errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        this.clearSession();
        return { success: false, user: null };
      }

      // Update session with new token
      authStore.setSession(result.data.sessionToken, result.data.expiresAt);

      // Verify the new session to get updated user data
      const verifyResult = await authApi.verifySession();

      if (isErrorResponse(verifyResult)) {
        this.clearSession();
        return { success: false, user: null };
      }

      if (!isStandardResponse(verifyResult) || !verifyResult.data) {
         errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        this.clearSession();
        return { success: false, user: null };
      }

      // Update cached user data
      authStore.setUserData(verifyResult.data);
      return { success: true, user: verifyResult.data };

    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to refresh session. Using cached data.'
      );

      // Try to get cached user data
      const cachedUser = authStore.getUserData();
      return {
        success: !!cachedUser,
        user: cachedUser
      };
    }
  }

  /**
   * Clear all user data from local storage and session storage.
   * This includes auth data, prompts, configured models, and configured repos.
   * @private
   */
  private clearAllUserData(): void {
    try {
      if (typeof window !== 'undefined') {
        // Clear auth-related data
        this.clearSession();
        
        // Clear application data
        Object.values(LOCAL_STORAGE_KEYS).forEach(key => {
          localStorage.removeItem(key);
        });
        
        // Clear any remaining session storage items
        sessionStorage.clear();
        
        console.log('All user data cleared successfully');
      }
    } catch (error) {
      console.error('Error clearing user data:', error);
    }
  }
}

// Export singleton instance
export const authService = new AuthService();

// Export class for testing or custom instances
export default authService;