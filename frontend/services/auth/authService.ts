import { authApi } from './api';
import { errorNotification } from '@/lib/notifications';
import { LOCAL_STORAGE_KEYS } from '@/utils/localStorageConstants';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { User, LoginResponse } from './types';

/**
 * Authentication service that handles all authentication-related operations.
 * This includes session management, user data handling, and interactions with the auth API.
 * Following single responsibility principle - only handles auth concerns.
 */
export class AuthService {

  /**
   * Get the authorization URL for initiating the OAuth flow.
   * @param promptrepoRedirectUrl - Optional PromptRepo app URL to redirect after login.
   * @returns The authorization URL or null if an error occurs.
   */
  async getAuthUrl(promptrepoRedirectUrl?: string): Promise<string> {
    try {
      const result = await authApi.initiateLogin(promptrepoRedirectUrl);

      if (isErrorResponse(result)) {
        throw new Error("Failed to get auth URL");
      }

      if (!isStandardResponse(result) || !result.data) {
        throw new Error("Failed to get auth URL");
      }

      return result.data.authUrl;

    } catch (error: unknown) {
        throw error;
    }
  }

  /**
   * Handles the authentication callback from the OAuth provider.
   * Exchanges the authorization code for a session token and stores the session.
   * @param code - The authorization code from the OAuth provider.
   * @param state - The state parameter from the OAuth provider.
   * @returns The login response data with optional promptrepoRedirectUrl or null if an error occurs.
   */
  async handleCallback(code: string, state: string): Promise<LoginResponse> {
    try {
      const result = await authApi.handleGithubCallback(code, state);

      if (isErrorResponse(result)) {
        throw result;
      }

      if (!isStandardResponse(result) || !result.data) {
         throw result;
      }

      // Return the full response - the store will handle storing the data
      return result.data;

    } catch (error: unknown) {
      throw error;
    }
  }

  /**
   * Logs out the current user by invalidating the session on the server and clearing local data.
   * @returns true if the logout was successful (client-side), false otherwise.
   */
  async logout(): Promise<boolean> {
    try {
      // Attempt to invalidate session on server
      const result = await authApi.logout();

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Logout Error',
          result.detail || 'Could not complete logout on server. Clearing local session.'
        );
      }
      
      // Clear all local data regardless of server response
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
      const result = await authApi.refreshSession();

      if (isErrorResponse(result)) {
        errorNotification(
          result.title || 'Session Refresh Failed',
          result.detail || 'Could not refresh your session. Please log in again.'
        );
        return { success: false, user: null };
      }

      if (!isStandardResponse(result) || !result.data) {
         errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        return { success: false, user: null };
      }

      // Verify the new session to get updated user data
      const verifyResult = await authApi.verifySession();

      if (isErrorResponse(verifyResult)) {
        return { success: false, user: null };
      }

      if (!isStandardResponse(verifyResult) || !verifyResult.data) {
         errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        return { success: false, user: null };
      }

      return { success: true, user: verifyResult.data };

    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to refresh session. Using cached data.'
      );

      return { success: false, user: null };
    }
  }

  /**
   * Checks the current authentication status by verifying the session with the backend.
   * @returns An object indicating success and the user data if successful.
   */
  async checkAuthStatus(): Promise<{ success: boolean; user: User | null }> {
    try {
      const result = await authApi.verifySession();

      if (isErrorResponse(result)) {
        // If it's a 401, it's not an error, just an unauthenticated state.
        // The global interceptor will handle clearing the store.
        if (result.status_code === 401) {
          return { success: false, user: null };
        }
        // For other errors, show a notification.
        errorNotification(
          result.title || 'Authentication Check Failed',
          result.detail || 'Could not verify your session. Please log in again.'
        );
        return { success: false, user: null };
      }

      if (!isStandardResponse(result) || !result.data) {
        errorNotification(
          'Unexpected Response',
          'Received an unexpected response from the server.'
        );
        return { success: false, user: null };
      }

      return { success: true, user: result.data };

    } catch (error: unknown) {
      errorNotification(
        'Connection Error',
        'Unable to verify session. Please check your connection.'
      );
      return { success: false, user: null };
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
        // Clear application data
        Object.values(LOCAL_STORAGE_KEYS).forEach(key => {
          localStorage.removeItem(key);
        });
        
        // Clear auth store from session storage
        sessionStorage.removeItem('auth-store');
        
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