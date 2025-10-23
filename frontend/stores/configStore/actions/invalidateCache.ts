import { StateCreator } from '@/lib/zustand';
import type { ConfigStore, ConfigActions } from '../types';
import { initialConfigState } from '../state';

export const createInvalidateCacheAction: StateCreator<ConfigStore, [], [], Pick<ConfigActions, 'invalidateCache'>> = (set, get, api) => ({
  invalidateCache: async () => {
    console.log('Config cache invalidated - clearing localStorage and resetting state');
    
    // Clear localStorage storage first to prevent rehydration
    try {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('config-store');
        console.log('Cleared config-store from localStorage');
      }
    } catch (err) {
      console.error('Failed to clear localStorage:', err);
    }
    
    // Reset to initial state
    set((draft) => {
      Object.assign(draft, initialConfigState);
    // @ts-expect-error - Immer middleware supports 3 params
    }, false, 'config/invalidate-cache');
    
    // Fetch fresh config from backend
    try {
      await get().getConfig();
    } catch (err) {
      console.error('Failed to refresh config after cache invalidation:', err);
    }
  },
});