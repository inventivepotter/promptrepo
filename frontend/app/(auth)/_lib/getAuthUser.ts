import type { User } from '../_types/AuthState';
import mockAuthData from './mockAuthData.json';
import { authApi } from './api/authApi';
import { errorNotification } from '@/lib/notifications';
import { storageState } from '../_state/storageState';

export const getMockAuthUser = (): User => {
  return mockAuthData.user;
};

export async function getAuthUser(): Promise<User | null> {
  try {
    const currentSessionToken = storageState.getSessionToken();
    if (!currentSessionToken) {
      return null;
    }

    const result = await authApi.verifySession(currentSessionToken);

    if (!result.success) {
      errorNotification(
        result.error || 'Session Verification Failed',
        result.message || 'Could not verify user session. Please log in again.'
      );

      storageState.clearSession();
      // TODO: Remove after Auth testing
      // If no cached data and in development, return mock data
      if (process.env.NODE_ENV === 'development') {
        const mockUser = getMockAuthUser();
        const mockSessionToken = 'mock_session_token';
        const mockExpiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
        
        storageState.setSession(mockSessionToken, mockExpiresAt);
        storageState.setUserData(mockUser);
        
        return mockUser;
      }
      return null;
    }

    // Store verified user data and refresh session
    storageState.setUserData(result.data);
    
    // Re-store session with a new expiry time to keep it fresh
    const newExpiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(); // 24 hours
    storageState.setSession(currentSessionToken, newExpiresAt);
    
    return result.data;

  } catch (error: unknown) {
    errorNotification(
      'Connection Error',
      'Unable to verify user session. Using cached data.'
    );
    
    // Try to get cached user data from session storage
    const cachedUser = storageState.getUserData();
    const currentSessionToken = storageState.getSessionToken();
    
    if (cachedUser) {
      // If we have cached user data, ensure session is still stored
      if (currentSessionToken) {
        const newExpiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
        storageState.setSession(currentSessionToken, newExpiresAt);
      }
      return cachedUser;
    }
    
    // TODO: Remove after Auth testing
    // If no cached data and in development, return mock data
    if (process.env.NODE_ENV === 'development') {
      const mockUser = getMockAuthUser();
      const mockSessionToken = 'mock_session_token';
      const mockExpiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();
      
      storageState.setSession(mockSessionToken, mockExpiresAt);
      storageState.setUserData(mockUser);
      
      return mockUser;
    }

    return null;
  }
}