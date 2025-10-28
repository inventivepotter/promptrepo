/**
 * Metrics Store - Main store file for metric metadata management
 */
import { create } from 'zustand';
import { devtools, immer } from '@/lib/zustand';
import { initialMetricsState } from './state';
import { createMetricsActions } from './actions';
import type { MetricsStore } from './types';

/**
 * Create the metrics store with middleware
 * No persistence needed - metadata should be fresh from server
 */
export const useMetricsStore = create<MetricsStore>()(
  devtools(
    immer((set, get, ...rest) => {
      return {
        ...initialMetricsState,
        ...createMetricsActions(set, get, ...rest),
      };
    }),
    {
      name: 'metrics-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);