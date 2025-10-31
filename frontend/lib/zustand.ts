import { StateCreator } from 'zustand';
import { devtools } from 'zustand/middleware';
import { persist, createJSONStorage, StateStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import { get, set, del } from 'idb-keyval';
import { errorNotification } from './notifications';
import { ErrorResponse, isErrorResponse } from '@/types/OpenApiResponse';

// =============================================================================
// Error Handling Utilities  
// =============================================================================

export interface StoreError {
  code: string;
  message: string;
  timestamp: Date;
  context?: Record<string, unknown>;
}

export const handleStoreError = (error: unknown, context?: string): StoreError => {
  const timestamp = new Date();

  if (isErrorResponse(error as ErrorResponse)) {
    const errorDetails = error as ErrorResponse;
    errorNotification(
      errorDetails.title || 'Unknown Error',
      errorDetails.detail || 'An unknown error occurred.'
    );
  }
  
  if (error instanceof Error) {
    return {
      code: 'STORE_ERROR',
      message: error.message,
      timestamp,
      context: context ? { action: context } : undefined,
    };
  }
  return {
    code: 'UNKNOWN_ERROR',
    message: 'An unknown error occurred',
    timestamp,
    context: context ? { action: context, originalError: error } : { originalError: error },
  };
};

// =============================================================================
// Development Utilities
// =============================================================================

export const logStoreAction = (storeName: string, action: string, payload?: unknown) => {
  if (process.env.NODE_ENV === 'development') {
    console.group(`🔄 ${storeName} - ${action}`);
    if (payload !== undefined) {
      console.log('Payload:', payload);
    }
    console.log('Timestamp:', new Date().toISOString());
    console.groupEnd();
  }
};

// =============================================================================
// Storage Helper Functions
// =============================================================================

/**
 * Alternative storage configurations for different use cases
 */

// For longer persistence (survives browser restarts)
export const createLocalStorage = (name: string) => ({
  name,
  storage: createJSONStorage(() => localStorage),
});

// For sensitive data that should clear on tab close
export const createSessionStorage = (name: string) => ({
  name,
  storage: createJSONStorage(() => sessionStorage),
});

// For testing environments
export const createMemoryStorage = (name: string) => {
  const memoryStorage = new Map<string, string>();
  return {
    name,
    storage: {
      getItem: (name: string) => {
        const value = memoryStorage.get(name);
        return value ? JSON.parse(value) : null;
      },
      setItem: (name: string, value: unknown) => {
        memoryStorage.set(name, JSON.stringify(value));
      },
      removeItem: (name: string) => {
        memoryStorage.delete(name);
      },
    },
  };
};

// For IndexedDB storage (better for larger datasets)
export const createIndexedDBStorage = (name: string) => {
  const storage: StateStorage = {
    getItem: async (key: string): Promise<string | null> => {
      // Skip IndexedDB operations during SSR
      if (typeof window === 'undefined') {
        return null;
      }
      
      try {
        const value = await get(key);
        return value || null;
      } catch (error) {
        console.error(`Failed to get item ${key} from IndexedDB:`, error);
        return null;
      }
    },
    setItem: async (key: string, value: string): Promise<void> => {
      // Skip IndexedDB operations during SSR
      if (typeof window === 'undefined') {
        return;
      }
      
      try {
        await set(key, value);
      } catch (error) {
        console.error(`Failed to set item ${key} in IndexedDB:`, error);
      }
    },
    removeItem: async (key: string): Promise<void> => {
      // Skip IndexedDB operations during SSR
      if (typeof window === 'undefined') {
        return;
      }
      
      try {
        await del(key);
      } catch (error) {
        console.error(`Failed to remove item ${key} from IndexedDB:`, error);
      }
    },
  };

  return {
    name,
    storage: createJSONStorage(() => storage),
  };
};

// =============================================================================
// Middleware Re-exports
// =============================================================================

export { devtools, persist, immer, createJSONStorage };
export type { StateCreator, StateStorage };