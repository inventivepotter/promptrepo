/**
 * Types for Metrics Store
 */
import type { MetricMetadata, MetricsMetadataResponse } from '@/types/eval';

/**
 * Metrics Store State
 */
export interface MetricsState {
  /** Metrics metadata keyed by metric type */
  metadata: MetricsMetadataResponse | null;
  /** Loading state */
  isLoading: boolean;
  /** Error message */
  error: string | null;
}

/**
 * Metrics Store Actions
 */
export interface MetricsActions {
  /** Fetch metrics metadata from API */
  fetchMetadata: () => Promise<void>;
  /** Get metadata for specific metric type */
  getMetricMetadata: (metricType: string) => MetricMetadata | null;
  /** Get required expected fields for a metric */
  getRequiredExpectedFields: (metricType: string) => string[];
  /** Get required actual fields for a metric */
  getRequiredActualFields: (metricType: string) => string[];
  /** Check if metric is deterministic */
  isDeterministic: (metricType: string) => boolean;
  /** Check if metric is non-deterministic (requires LLM) */
  isNonDeterministic: (metricType: string) => boolean;
  /** Clear metrics data */
  clearMetadata: () => void;
}

/**
 * Combined Metrics Store type
 */
export type MetricsStore = MetricsState & MetricsActions;