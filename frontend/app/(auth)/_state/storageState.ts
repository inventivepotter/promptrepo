interface StorageData {
  sessionToken: string;
  expiresAt: string;
  createdAt: string;
}

interface UserStorageData {
  id: string;
  login: string;
  name: string;
  email: string;
  avatar_url: string;
  html_url: string;
  created_at: string;
  updated_at: string;
}

const getInitialSession = (): StorageData | null => {
  if (typeof window === 'undefined') return null;
  try {
    const data = localStorage.getItem('auth_session');
    if (!data) return null;
    
    const session = JSON.parse(data);
    if (new Date() > new Date(session.expiresAt)) {
      localStorage.removeItem('auth_session');
      sessionStorage.removeItem('user_data');
      return null;
    }
    return session;
  } catch {
    return null;
  }
};

const getInitialUser = (): UserStorageData | null => {
  if (typeof window === 'undefined') return null;
  try {
    const data = sessionStorage.getItem('user_data');
    return data ? JSON.parse(data) : null;
  } catch {
    return null;
  }
};

export const storageState = {
  // Session Storage Keys
  SESSION_KEY: 'auth_session',
  USER_KEY: 'user_data',
  REFRESH_TOKEN_KEY: 'refresh_token',

  // Initial State
  getInitialState: () => {
    const session = getInitialSession();
    const user = getInitialUser();
    
    return {
      isAuthenticated: !!(session?.sessionToken && user),
      isLoading: false,
      user,
      sessionToken: session?.sessionToken || null
    };
  },

  // Session Management
  setSession: (sessionToken: string, expiresAt: string): void => {
    try {
      if (typeof window === 'undefined') return;
      
      const sessionData: StorageData = {
        sessionToken,
        expiresAt,
        createdAt: new Date().toISOString()
      };
      
      localStorage.setItem(storageState.SESSION_KEY, JSON.stringify(sessionData));
    } catch (error) {
      console.error('Failed to set session:', error);
      throw new Error('Failed to store session');
    }
  },

  getSession: (): StorageData | null => {
    try {
      if (typeof window === 'undefined') return null;
      
      const data = localStorage.getItem(storageState.SESSION_KEY);
      if (!data) return null;

      const session = JSON.parse(data);
      if (new Date() > new Date(session.expiresAt)) {
        storageState.clearSession();
        storageState.clearUserData();
        return null;
      }

      return session;
    } catch (error) {
      console.error('Failed to get session:', error);
      return null;
    }
  },

  getSessionToken: (): string | null => {
    const session = storageState.getSession();
    return session?.sessionToken || null;
  },

  clearSession: (): void => {
    try {
      if (typeof window === 'undefined') return;
      localStorage.removeItem(storageState.SESSION_KEY);
      localStorage.removeItem(storageState.REFRESH_TOKEN_KEY);
    } catch (error) {
      console.error('Failed to clear session:', error);
    }
  },

  getSessionExpiry: (): Date | null => {
    const session = storageState.getSession();
    return session ? new Date(session.expiresAt) : null;
  },

  shouldRefreshSession: (): boolean => {
    const expiry = storageState.getSessionExpiry();
    if (!expiry) return false;
    
    const oneHourFromNow = new Date(Date.now() + 60 * 60 * 1000);
    return expiry < oneHourFromNow;
  },

  // User Data Management
  setUserData: (userData: UserStorageData): void => {
    try {
      if (typeof window === 'undefined') return;
      sessionStorage.setItem(storageState.USER_KEY, JSON.stringify(userData));
    } catch (error) {
      console.error('Failed to store user data:', error);
    }
  },

  getUserData: (): UserStorageData | null => {
    try {
      if (typeof window === 'undefined') return null;
      
      const data = sessionStorage.getItem(storageState.USER_KEY);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Failed to get user data:', error);
      return null;
    }
  },

  clearUserData: (): void => {
    try {
      if (typeof window === 'undefined') return;
      sessionStorage.removeItem(storageState.USER_KEY);
    } catch (error) {
      console.error('Failed to clear user data:', error);
    }
  }
};

export default storageState;