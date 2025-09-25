/**
 * Auth Store Utilities
 * 
 * Testing utilities and helper functions for auth store.
 * Useful for testing, debugging, and store management.
 */

import { useAuthStore } from './store';
import type { AuthStore } from './types';

/**
 * Reset auth store to initial state
 * Useful for testing and cleanup
 */
export const resetAuthStore = () => {
  useAuthStore.setState({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    sessionToken: null,
    error: null,
  });
};

/**
 * Get current auth state
 * Useful for testing and debugging
 */
export const getAuthState = (): AuthStore => {
  return useAuthStore.getState();
};

/**
 * Subscribe to auth state changes
 * Returns unsubscribe function
 */
export const subscribeToAuth = (
  callback: (state: AuthStore) => void
): (() => void) => {
  return useAuthStore.subscribe(callback);
};

/**
 * Subscribe to specific auth property changes
 * Returns unsubscribe function
 */
export const subscribeToAuthProperty = <K extends keyof AuthStore>(
  property: K,
  callback: (value: AuthStore[K]) => void
): (() => void) => {
  let previousValue = useAuthStore.getState()[property];
  
  return useAuthStore.subscribe((state) => {
    const currentValue = state[property];
    if (currentValue !== previousValue) {
      previousValue = currentValue;
      callback(currentValue);
    }
  });
};

/**
 * Wait for auth initialization
 * Useful for ensuring auth is ready before proceeding
 */
export const waitForAuth = async (timeout = 5000): Promise<boolean> => {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeout) {
    const state = getAuthState();
    if (!state.isLoading) {
      return true;
    }
    await new Promise(resolve => setTimeout(resolve, 100));
  }
  
  return false;
};

/**
 * Check if user has a valid session
 */
export const hasValidSession = (): boolean => {
  const state = getAuthState();
  return state.isAuthenticated && !!state.sessionToken;
};

/**
 * Get current user or null
 */
export const getCurrentUser = () => {
  return getAuthState().user;
};

/**
 * Debug utility to log current auth state
 */
export const logAuthState = () => {
  const state = getAuthState();
  console.group('🔐 Auth Store State');
  console.log('User:', state.user);
  console.log('Authenticated:', state.isAuthenticated);
  console.log('Session Token:', state.sessionToken ? '***' : 'null');
  console.log('Loading:', state.isLoading);
  console.log('Error:', state.error);
  console.groupEnd();
};

/**
 * Testing utility to set auth state directly
 * WARNING: Only use for testing purposes
 */
export const setAuthStateForTesting = (partialState: Partial<AuthStore>) => {
  if (process.env.NODE_ENV !== 'test' && process.env.NODE_ENV !== 'development') {
    console.warn('setAuthStateForTesting should only be used in test/dev environments');
    return;
  }
  useAuthStore.setState(partialState);
};