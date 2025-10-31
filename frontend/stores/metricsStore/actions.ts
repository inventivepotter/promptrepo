/**
 * Actions for Metrics Store
 */
import type { StateCreator } from 'zustand';
import EvalApi from '@/services/evals/api';
import { handleStoreError } from '@/lib/zustand';
import { isStandardResponse, isErrorResponse } from '@/types/OpenApiResponse';
import type { MetricsStore, MetricsActions } from './types';
import type { MetricMetadata } from '@/types/eval';

export const createMetricsActions: StateCreator<
  MetricsStore,
  [['zustand/devtools', never], ['zustand/immer', never]],
  [],
  MetricsActions
> = (set, get) => ({
  fetchMetadata: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await EvalApi.getMetricsMetadata();
      
      if (isStandardResponse(response) && response.data) {
        set({ metadata: response.data, isLoading: false });
      } else if (isErrorResponse(response)) {
        throw new Error(response.detail || response.title || 'Failed to fetch metrics metadata');
      } else {
        throw new Error('Failed to fetch metrics metadata');
      }
    } catch (error) {
      const storeError = handleStoreError(error, 'fetchMetadata');
      set({ error: storeError.message, isLoading: false });
    }
  },

  getMetricMetadata: (metricType: string): MetricMetadata | null => {
    const { metadata } = get();
    if (!metadata) return null;
    return metadata[metricType] || null;
  },

  getRequiredExpectedFields: (metricType: string): string[] => {
    const metadata = get().getMetricMetadata(metricType);
    return metadata?.required_expected_fields || [];
  },

  getRequiredActualFields: (metricType: string): string[] => {
    const metadata = get().getMetricMetadata(metricType);
    return metadata?.required_actual_fields || [];
  },

  isDeterministic: (metricType: string): boolean => {
    const metadata = get().getMetricMetadata(metricType);
    return metadata?.category === 'deterministic';
  },

  isNonDeterministic: (metricType: string): boolean => {
    const metadata = get().getMetricMetadata(metricType);
    return metadata?.category === 'non_deterministic';
  },

  clearMetadata: () => {
    set({ metadata: null, error: null });
  },
});