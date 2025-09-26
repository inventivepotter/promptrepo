// Actions for Loading Store
import type { LoadingStore } from './types';
import type { StoreApi } from 'zustand';

export const createLoadingActions = (
  set: (fn: (state: LoadingStore) => Partial<LoadingStore>) => void,
  get: () => LoadingStore,
  api: StoreApi<LoadingStore>
) => ({
  showLoading: (title = "Processing...", message = "Please wait while we process your request") => {
    set(() => ({
      isLoading: true,
      title,
      message,
    }));
  },
  
  hideLoading: () => {
    set(() => ({
      isLoading: false,
    }));
  },
});