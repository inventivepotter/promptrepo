import { authApi } from './api/authApi';
import { errorNotification } from '@/lib/notifications';
import { storageState } from '../_state/storageState';
import { LOCAL_STORAGE_KEYS } from '../../../utils/localStorageConstants';

/**
 * Clear all user data from local storage and session storage
 * This includes auth data, prompts, configured models, and configured repos
 */
const clearAllUserData = (): void => {
  try {
    if (typeof window !== 'undefined') {
      // Clear auth-related data
      storageState.clearSession();
      storageState.clearUserData();
      
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
};

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
    
    // Always clear all local data regardless of server response
    clearAllUserData();
    
    return true;

  } catch (error: unknown) {
    errorNotification(
      'Connection Error',
      'Unable to complete server logout. Clearing local session.'
    );
    
    // Clear all local data even if server request fails
    clearAllUserData();
    
    return true;
  }
}