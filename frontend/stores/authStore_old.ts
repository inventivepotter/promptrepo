import type { components } from "@/types/generated/api";
import { localStorage } from "@/lib/localStorage";
import { LOCAL_STORAGE_KEYS } from "@/utils/localStorageConstants";

export type User = components['schemas']['User'];

interface StorageData {
  sessionToken: string;
  expiresAt: string;
  createdAt: string;
}

// Use the centralized storage keys
const STORE_NAME = LOCAL_STORAGE_KEYS;

/**
 * Session Management Functions
 */

/**
 * Store session data to localStorage
 * @param sessionToken - Session token
 * @param expiresAt - Session expiry date
 */
export const setSession = (sessionToken: string, expiresAt: string): void => {
  try {
    if (typeof window === 'undefined') return;
    
    const sessionData: StorageData = {
      sessionToken,
      expiresAt,
      createdAt: new Date().toISOString()
    };
    
    localStorage.set(STORE_NAME.AUTH_SESSION, sessionData);
  } catch (error) {
    console.error('Failed to set session:', error);
    throw new Error('Failed to store session');
  }
};

/**
 * Get session data from localStorage
 * @returns Session data if valid and not expired, null otherwise
 */
export const getSession = (): StorageData | null => {
  try {
    if (typeof window === 'undefined') return null;
    
    const session = localStorage.get<StorageData>(STORE_NAME.AUTH_SESSION);
    if (!session) return null;

    // Check if session is expired
    if (new Date() > new Date(session.expiresAt)) {
      clearSession();
      return null;
    }

    return session;
  } catch (error) {
    console.error('Failed to get session:', error);
    return null;
  }
};

/**
 * Get session token directly
 * @returns Session token if valid, null otherwise
 */
export const getSessionToken = (): string | null => {
  const session = getSession();
  return session?.sessionToken || null;
};

/**
 * Clear session data from localStorage
 */
export const clearSession = (): void => {
  localStorage.clear(STORE_NAME.AUTH_SESSION);
  localStorage.clear(STORE_NAME.REFRESH_TOKEN);
};

/**
 * Get session expiry date
 * @returns Date object of session expiry, null if no session
 */
export const getSessionExpiry = (): Date | null => {
  const session = getSession();
  return session ? new Date(session.expiresAt) : null;
};

/**
 * Check if session should be refreshed (expires within 1 hour)
 * @returns boolean indicating if session needs refresh
 */
export const shouldRefreshSession = (): boolean => {
  const session = getSession();
  if (!session) return false;
  
  const expiry = new Date(session.expiresAt);
  const oneHourFromNow = new Date(Date.now() + 60 * 60 * 1000);
  return expiry < oneHourFromNow;
};

/**
 * Update session expiry
 * @param newExpiresAt - New expiry date
 */
export const updateSessionExpiry = (newExpiresAt: string): void => {
  const session = getSession();
  if (session) {
    const updatedSession = { ...session, expiresAt: newExpiresAt };
    localStorage.set(STORE_NAME.AUTH_SESSION, updatedSession);
  }
};

/**
 * User Data Management Functions
 */

/**
 * Store user data to sessionStorage (for security)
 * @param userData - User data to store
 */
export const setUserData = (userData: User): void => {
  try {
    if (typeof window === 'undefined') return;
    sessionStorage.setItem(STORE_NAME.USER_DATA, JSON.stringify(userData));
  } catch (error) {
    console.error('Failed to store user data:', error);
  }
};

/**
 * Get user data from sessionStorage
 * @returns User data if found, null otherwise
 */
export const getUserData = (): User | null => {
  try {
    if (typeof window === 'undefined') return null;
    
    const data = sessionStorage.getItem(STORE_NAME.USER_DATA);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Failed to get user data:', error);
    return null;
  }
};

/**
 * Clear user data from sessionStorage
 */
export const clearUserData = (): void => {
  try {
    if (typeof window === 'undefined') return;
    sessionStorage.removeItem(STORE_NAME.USER_DATA);
  } catch (error) {
    console.error('Failed to clear user data:', error);
  }
};

/**
 * Refresh Token Management
 */

/**
 * Store refresh token
 * @param refreshToken - Refresh token to store
 */
export const setRefreshToken = (refreshToken: string): void => {
  localStorage.set(STORE_NAME.REFRESH_TOKEN, refreshToken);
};

/**
 * Get refresh token
 * @returns Refresh token if exists, null otherwise
 */
export const getRefreshToken = (): string | null => {
  return localStorage.get<string>(STORE_NAME.REFRESH_TOKEN);
};

/**
 * Clear refresh token
 */
export const clearRefreshToken = (): void => {
  localStorage.clear(STORE_NAME.REFRESH_TOKEN);
};

/**
 * Combined Authentication Functions
 */

/**
 * Create session with token and expiry
 * @param sessionToken - Session token
 * @param expiresAt - Session expiry date
 * @param user - Optional user data to store
 */
export const createSession = (sessionToken: string, expiresAt: string, user?: User): void => {
  setSession(sessionToken, expiresAt);
  if (user) {
    setUserData(user);
  }
};

/**
 * Check if user is currently authenticated
 * @returns boolean indicating authentication status
 */
export const isUserAuthenticated = (): boolean => {
  const session = getSession();
  const user = getUserData();
  return !!(session?.sessionToken && user);
};

/**
 * Clear all authentication data
 */
export const clearAllAuthData = (): void => {
  clearSession();
  clearUserData();
};

/**
 * Get initial authentication state for app startup
 * @returns Object with authentication state
 */
export const getInitialAuthState = () => {
  const session = getSession();
  const user = getUserData();
  
  return {
    isAuthenticated: !!(session?.sessionToken && user),
    isLoading: false,
    user,
    sessionToken: session?.sessionToken || null
  };
};