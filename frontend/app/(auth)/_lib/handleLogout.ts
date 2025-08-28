import { authApi } from './api/authApi';
import { errorNotification } from '@/lib/notifications';
import { storageState } from '../_state/storageState';

export async function handleLogout(): Promise<boolean> {
  try {
    const sessionToken = storageState.getSessionToken();
    
    if (sessionToken) {
      // Attempt to invalidate session on server
      const result = await authApi.logout(sessionToken);

      if (!result.success) {
        errorNotification(
          result.error || 'Logout Error',
          result.message || 'Could not complete logout on server. Clearing local session.'
        );
      }
    }

    // In development, just clear local data
    if (process.env.NODE_ENV === 'development') {
      storageState.clearSession();
      storageState.clearUserData();
      return true;
    }

    // Always clear local session data regardless of server response
    storageState.clearSession();
    storageState.clearUserData();
    
    return true;

  } catch (error: unknown) {
    errorNotification(
      'Connection Error',
      'Unable to complete server logout. Clearing local session.'
    );
    
    // Clear local session even if server request fails
    storageState.clearSession();
    storageState.clearUserData();
    
    return true;
  }
}