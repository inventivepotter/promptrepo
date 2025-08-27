import type { User } from '../_types/AuthState';
import { authApi } from './api/authApi';
import { errorNotification } from '@/lib/notifications';
import { storageState } from '../_state/storageState';
import { getMockAuthUser } from './getAuthUser';

interface RefreshResult {
  success: boolean;
  user: User | null;
}

export async function refreshAuthSession(): Promise<RefreshResult> {
  try {
    const sessionToken = storageState.getSessionToken();
    if (!sessionToken) {
      return { success: false, user: null };
    }

    // Only refresh if needed
    if (!storageState.shouldRefreshSession()) {
      const cachedUser = storageState.getUserData();
      return { success: true, user: cachedUser };
    }

    const result = await authApi.refreshSession(sessionToken);

    if (!result.success) {
      errorNotification(
        result.error || 'Session Refresh Failed',
        result.message || 'Could not refresh your session. Please log in again.'
      );

      // In development, extend mock session
      if (process.env.NODE_ENV === 'development') {
        const mockUser = getMockAuthUser();
        const newExpiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(); // 24 hours
        
        storageState.setSession('mock_session_token', newExpiresAt);
        storageState.setUserData(mockUser);
        
        return { success: true, user: mockUser };
      }

      storageState.clearSession();
      storageState.clearUserData();
      return { success: false, user: null };
    }

    // Update session with new token
    storageState.setSession(result.data.sessionToken, result.data.expiresAt);

    // Verify the new session to get updated user data
    const verifyResult = await authApi.verifySession(result.data.sessionToken);

    if (!verifyResult.success) {
      storageState.clearSession();
      storageState.clearUserData();
      return { success: false, user: null };
    }

    // Update cached user data
    storageState.setUserData(verifyResult.data);
    return { success: true, user: verifyResult.data };

  } catch (error: unknown) {
    errorNotification(
      'Connection Error',
      'Unable to refresh session. Using cached data.'
    );

    // In development, extend mock session
    if (process.env.NODE_ENV === 'development') {
      const mockUser = getMockAuthUser();
      const newExpiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(); // 24 hours
      
      storageState.setSession('mock_session_token', newExpiresAt);
      storageState.setUserData(mockUser);
      
      return { success: true, user: mockUser };
    }

    // Try to get cached user data
    const cachedUser = storageState.getUserData();
    return { 
      success: !!cachedUser,
      user: cachedUser 
    };
  }
}