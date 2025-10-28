/**
 * TypeScript types for DeepEval Test Framework
 * Re-exports types from generated API and adds additional helper types
 */

import type { components } from '@/types/generated/api';

// Re-export generated types from OpenAPI schema
export type MetricConfig = components['schemas']['MetricConfig'];
export type MetricResult = components['schemas']['MetricResult'];
export type TestSuiteExecutionResult = components['schemas']['TestSuiteExecutionResult'];
export type UnitTestExecutionResult = components['schemas']['UnitTestExecutionResult'];
export type TestSuiteSummary = components['schemas']['TestSuiteSummary'];
export type ExpectedEvaluationFieldsModel = components['schemas']['ExpectedEvaluationFieldsModel'];
export type ActualEvaluationFieldsModel = components['schemas']['ActualEvaluationFieldsModel'];
export type TestSuiteDefinition = components['schemas']['TestSuiteDefinition-Output'];
export type TestSuiteData = components['schemas']['TestSuiteData-Output'];
export type UnitTestDefinition = components['schemas']['UnitTestDefinition-Output'];
export type MetricType = components['schemas']['MetricType'];

// Re-export MetricMetadataModel from generated types
export type MetricMetadata = components['schemas']['MetricMetadataModel'];

/**
 * Response from metrics metadata endpoint
 * Maps metric type to its metadata
 */
export type MetricsMetadataResponse = Record<string, MetricMetadata>;

/**
 * Metric category types
 */
export type MetricCategory = 'deterministic' | 'non_deterministic';

/**
 * Helper type for metric configuration forms
 */
export interface MetricFormField {
  /** Field name */
  name: string;
  /** Field label for UI */
  label: string;
  /** Field type */
  type: string;
  /** Field description */
  description?: string;
  /** Whether field is required */
  required: boolean;
  /** Default value */
  defaultValue?: unknown;
  /** Allowed enum values */
  enumValues?: unknown[];
}