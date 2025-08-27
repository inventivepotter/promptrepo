import mockData from './authUrl.json';
import { authApi } from './api/authApi';
import { errorNotification } from '@/lib/notifications';

export const getMockAuthUrl = (): string => {
  return mockData.authUrl;
};

export async function getAuthUrl(): Promise<string | null> {
  try {
    const result = await authApi.initiateLogin();

    if (!result.success) {
      errorNotification(
        result.error || 'Login Failed',
        result.message || 'Could not initiate GitHub login. Please try again.'
      );

      // In development, return mock auth URL
      if (process.env.NODE_ENV === 'development') {
        return getMockAuthUrl();
      }

      return null;
    }

    return result.data.authUrl;

  } catch (error: unknown) {
    errorNotification(
      'Connection Error',
      'Unable to connect to authentication service. Using mock URL in development.'
    );
    
    // Return mock URL in development
    if (process.env.NODE_ENV === 'development') {
      return getMockAuthUrl();
    }

    return null;
  }
}