// Main loading store implementation
import { create } from 'zustand';
import { devtools, immer } from '@/lib/zustand';
import { createLoadingActions } from './actions';
import { initialLoadingState } from './state';
import type { LoadingStore } from './types';

// Create the loading store with middleware
export const useLoadingStore = create<LoadingStore>()(
  devtools(
    immer((set, get, api) => ({
      // Initial state
      ...initialLoadingState,
      
      // Actions
      ...createLoadingActions(set, get, api),
    })),
    {
      name: 'loading-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

// Export the store instance for direct access if needed
export default useLoadingStore;