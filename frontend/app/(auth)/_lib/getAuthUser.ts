import type { User } from "../../../types/User";
import { authApi } from './api/authApi';
import { errorNotification } from '@/lib/notifications';
import { storageState } from '../_state/storageState';

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

    return null;
  }
}