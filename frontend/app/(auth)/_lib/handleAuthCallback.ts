import type { LoginResponse } from '../_types/AuthState';
import { authApi } from './api/authApi';
import { errorNotification } from '@/lib/notifications';
import { storageState } from '../_state/storageState';

export async function handleAuthCallback(code: string, state: string): Promise<LoginResponse | null> {
  try {
    const result = await authApi.exchangeCodeForToken(code, state);

    if (!result.success) {
      errorNotification(
        result.error || 'Authentication Failed',
        result.message || 'Could not complete GitHub authentication. Please try again.'
      );
      return null;
    }

    // Store session and user data
    storageState.setSession(result.data.sessionToken, result.data.expiresAt);
    storageState.setUserData(result.data.user);
    
    return result.data;

  } catch (error: unknown) {
    errorNotification(
      'Connection Error',
      'Unable to complete authentication. Using mock data in development.'
    );
    return null;
  }
}