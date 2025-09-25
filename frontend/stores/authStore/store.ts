// Main auth store implementation
import { create } from 'zustand';
import { devtools, persist, immer } from '@/lib/zustand';
import { createAuthActions } from './actions';
import { initialAuthState } from './state';
import { authPersistConfig } from './storage';
import type { AuthStore } from './types';

// Create the auth store with middleware
export const useAuthStore = create<AuthStore>()(
  devtools(
    persist(
      immer((set, get, api) => ({
        // Initial state
        ...initialAuthState,
        
        // Actions
        ...createAuthActions(set, get, api),
      })),
      authPersistConfig
    ),
    {
      name: 'auth-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

// Export the store instance for direct access if needed
export default useAuthStore;