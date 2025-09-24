import type { components } from "@/types/generated/api";
import { localStorage } from "@/lib/localStorage";

export type User = components['schemas']['User'];

interface StorageData {
  sessionToken: string;
  expiresAt: string;
  createdAt: string;
}

// Storage keys for this module
const STORE_NAME = {
  AUTH_SESSION: 'auth_session',
  USER_DATA: 'user_data',
  REFRESH_TOKEN: 'refresh_token'
} as const;

/**
 * Store session data to localStorage
 * @param sessionData - Session data to store
 */
export const storeSessionData = (sessionData: StorageData): void => {
  localStorage.set(STORE_NAME.AUTH_SESSION, sessionData);
};

/**
 * Get session data from localStorage
 * @returns Session data if valid and not expired, null otherwise
 */
export const getSessionDataFromStorage = (): StorageData | null => {
  const session = localStorage.get<StorageData>(STORE_NAME.AUTH_SESSION);
  if (!session) return null;
  
  if (new Date() > new Date(session.expiresAt)) {
    clearSessionDataFromStorage();
    clearUserDataFromSessionStorage();
    return null;
  }
  return session;
};

/**
 * Clear session data from localStorage
 */
export const clearSessionDataFromStorage = (): void => {
  localStorage.clear(STORE_NAME.AUTH_SESSION);
  localStorage.clear(STORE_NAME.REFRESH_TOKEN);
};

/**
 * Store user data to sessionStorage (for security)
 * @param userData - User data to store
 */
export const storeUserDataToSessionStorage = (userData: User): void => {
  if (typeof window === 'undefined') return;
  try {
    sessionStorage.setItem(STORE_NAME.USER_DATA, JSON.stringify(userData));
  } catch (error) {
    console.error('Failed to store user data:', error);
  }
};

/**
 * Get user data from sessionStorage
 * @returns User data if found, null otherwise
 */
export const getUserDataFromSessionStorage = (): User | null => {
  if (typeof window === 'undefined') return null;
  try {
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
export const clearUserDataFromSessionStorage = (): void => {
  if (typeof window === 'undefined') return;
  try {
    sessionStorage.removeItem(STORE_NAME.USER_DATA);
  } catch (error) {
    console.error('Failed to clear user data:', error);
  }
};

/**
 * Create session with token and expiry
 * @param sessionToken - Session token
 * @param expiresAt - Session expiry date
 */
export const createSession = (sessionToken: string, expiresAt: string): void => {
  const sessionData: StorageData = {
    sessionToken,
    expiresAt,
    createdAt: new Date().toISOString()
  };
  storeSessionData(sessionData);
};

/**
 * Get current session token
 * @returns Session token if valid, null otherwise
 */
export const getCurrentSessionToken = (): string | null => {
  const session = getSessionDataFromStorage();
  return session?.sessionToken || null;
};

/**
 * Check if session should be refreshed (expires within 1 hour)
 * @returns boolean indicating if session needs refresh
 */
export const shouldRefreshSession = (): boolean => {
  const session = getSessionDataFromStorage();
  if (!session) return false;
  
  const expiry = new Date(session.expiresAt);
  const oneHourFromNow = new Date(Date.now() + 60 * 60 * 1000);
  return expiry < oneHourFromNow;
};

/**
 * Get session expiry date
 * @returns Date object of session expiry, null if no session
 */
export const getSessionExpiry = (): Date | null => {
  const session = getSessionDataFromStorage();
  return session ? new Date(session.expiresAt) : null;
};

/**
 * Check if user is currently authenticated
 * @returns boolean indicating authentication status
 */
export const isUserAuthenticated = (): boolean => {
  const session = getSessionDataFromStorage();
  const user = getUserDataFromSessionStorage();
  return !!(session?.sessionToken && user);
};

/**
 * Clear all authentication data
 */
export const clearAllAuthData = (): void => {
  clearSessionDataFromStorage();
  clearUserDataFromSessionStorage();
};

/**
 * Get initial authentication state for app startup
 * @returns Object with authentication state
 */
export const getInitialAuthState = () => {
  const session = getSessionDataFromStorage();
  const user = getUserDataFromSessionStorage();
  
  return {
    isAuthenticated: !!(session?.sessionToken && user),
    isLoading: false,
    user,
    sessionToken: session?.sessionToken || null
  };
};

/**
 * Update session expiry
 * @param newExpiresAt - New expiry date
 */
export const updateSessionExpiry = (newExpiresAt: string): void => {
  const session = getSessionDataFromStorage();
  if (session) {
    const updatedSession = { ...session, expiresAt: newExpiresAt };
    storeSessionData(updatedSession);
  }
};

/**
 * Store refresh token
 * @param refreshToken - Refresh token to store
 */
export const storeRefreshToken = (refreshToken: string): void => {
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