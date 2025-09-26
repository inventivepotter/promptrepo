// Initial state for Loading Store
import type { LoadingState } from './types';

export const initialLoadingState: LoadingState = {
  isLoading: false,
  title: "Processing...",
  message: "Please wait while we process your request",
};