import { AuthSession, User } from '../_types/AuthState';

const SESSION_COOKIE_NAME = 'auth_session';
const REFRESH_TOKEN_COOKIE_NAME = 'refresh_token';

export class SessionManager {
  // Set session in httpOnly, secure, SameSite cookie (via API route)
  static async setSession(sessionToken: string, expiresAt: string): Promise<void> {
    try {
      // In a real app, this would call an API route that sets httpOnly cookies
      // For now, we'll simulate it with localStorage (not secure, but for demo)
      const sessionData = {
        sessionToken,
        expiresAt,
        createdAt: new Date().toISOString()
      };
      
      if (typeof window !== 'undefined') {
        localStorage.setItem(SESSION_COOKIE_NAME, JSON.stringify(sessionData));
      }
    } catch (error) {
      console.error('Failed to set session:', error);
      throw new Error('Failed to store session');
    }
  }

  // Get session token from secure storage
  static getSessionToken(): string | null {
    try {
      if (typeof window === 'undefined') return null;
      
      const sessionData = localStorage.getItem(SESSION_COOKIE_NAME);
      if (!sessionData) return null;
      
      const parsed = JSON.parse(sessionData);
      
      // Check if session has expired
      if (new Date() > new Date(parsed.expiresAt)) {
        SessionManager.clearSession();
        return null;
      }
      
      return parsed.sessionToken;
    } catch (error) {
      console.error('Failed to get session token:', error);
      return null;
    }
  }

  // Check if user is authenticated
  static isAuthenticated(): boolean {
    const token = SessionManager.getSessionToken();
    return token !== null;
  }

  // Clear session (logout)
  static clearSession(): void {
    try {
      if (typeof window !== 'undefined') {
        localStorage.removeItem(SESSION_COOKIE_NAME);
        localStorage.removeItem(REFRESH_TOKEN_COOKIE_NAME);
      }
    } catch (error) {
      console.error('Failed to clear session:', error);
    }
  }

  // Get session expiry time
  static getSessionExpiry(): Date | null {
    try {
      if (typeof window === 'undefined') return null;
      
      const sessionData = localStorage.getItem(SESSION_COOKIE_NAME);
      if (!sessionData) return null;
      
      const parsed = JSON.parse(sessionData);
      return new Date(parsed.expiresAt);
    } catch (error) {
      console.error('Failed to get session expiry:', error);
      return null;
    }
  }

  // Check if session expires soon (within 1 hour)
  static shouldRefreshSession(): boolean {
    const expiry = SessionManager.getSessionExpiry();
    if (!expiry) return false;
    
    const oneHourFromNow = new Date(Date.now() + 60 * 60 * 1000);
    return expiry < oneHourFromNow;
  }

  // Store user data securely in session storage (cleared on tab close)
  static setUserData(user: User): void {
    try {
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('user_data', JSON.stringify(user));
      }
    } catch (error) {
      console.error('Failed to store user data:', error);
    }
  }

  // Get user data from session storage
  static getUserData(): User | null {
    try {
      if (typeof window === 'undefined') return null;
      
      const userData = sessionStorage.getItem('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Failed to get user data:', error);
      return null;
    }
  }

  // Clear user data
  static clearUserData(): void {
    try {
      if (typeof window !== 'undefined') {
        sessionStorage.removeItem('user_data');
      }
    } catch (error) {
      console.error('Failed to clear user data:', error);
    }
  }
}

export default SessionManager;