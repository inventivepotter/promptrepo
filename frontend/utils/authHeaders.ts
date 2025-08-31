import { storageState } from '../app/(auth)/_state/storageState';

// Helper function to get authentication headers
export const getAuthHeaders = () => {
  const sessionToken = storageState.getSessionToken();
  if (!sessionToken) {
    return {
        'Authorization': ''
    };
  }
  return {
    'Authorization': `Bearer ${sessionToken}`
  };
};