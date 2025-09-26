// Types for Loading Store
export interface LoadingState {
  isLoading: boolean;
  title: string;
  message: string;
}

export interface LoadingActions {
  showLoading: (title?: string, message?: string) => void;
  hideLoading: () => void;
}

export type LoadingStore = LoadingState & LoadingActions;