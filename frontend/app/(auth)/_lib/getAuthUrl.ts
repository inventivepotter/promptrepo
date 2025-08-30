import { authApi } from './api/authApi';
import { errorNotification } from '@/lib/notifications';

export async function getAuthUrl(): Promise<string | null> {
  try {
    const result = await authApi.initiateLogin();

    if (!result.success) {
      errorNotification(
        result.error || 'Login Failed',
        result.message || 'Could not initiate GitHub login. Please try again.'
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