/**
 * TypeScript types for DeepEval Test Framework
 * Mirrors backend Pydantic models from services/test/models.py
 */

/**
 * Predefined DeepEval metrics supported in UI
 */
export enum MetricType {
  ANSWER_RELEVANCY = 'answer_relevancy',
  FAITHFULNESS = 'faithfulness',
  CONTEXTUAL_RELEVANCY = 'contextual_relevancy',
  CONTEXTUAL_PRECISION = 'contextual_precision',
  CONTEXTUAL_RECALL = 'contextual_recall',
  HALLUCINATION = 'hallucination',
  BIAS = 'bias',
  TOXICITY = 'toxicity'
}

/**
 * Configuration for a single DeepEval metric
 */
export interface MetricConfig {
  /** Type of DeepEval metric */
  type: MetricType;
  /** Minimum passing score (0.0 to 1.0) */
  threshold: number;
  /** LLM model for metric evaluation */
  model: string;
  /** Include reasoning in results */
  include_reason: boolean;
  /** Enable strict evaluation mode */
  strict_mode: boolean;
}

/**
 * Individual test case definition
 */
export interface UnitTestDefinition {
  /** Unique test name within suite */
  name: string;
  /** Test description */
  description?: string;
  /** Name of the test suite this test belongs to */
  test_suite_name: string;
  /** Reference to prompt file path */
  prompt_reference: string;
  /** Template variables for prompt execution */
  template_variables: Record<string, unknown>;
  /** Expected output for comparison */
  expected_output?: string | null;
  /** DeepEval metrics to evaluate */
  metrics?: MetricConfig[];
  /** Whether test is enabled */
  enabled: boolean;
}

/**
 * Test suite containing multiple unit tests
 */
export interface TestSuiteDefinition {
  /** Test suite name */
  name: string;
  /** Suite description */
  description?: string;
  /** Unit tests in this suite */
  tests: UnitTestDefinition[];
  /** Tags for organization */
  tags: string[];
  /** ISO timestamp when suite was created */
  created_at: string;
  /** ISO timestamp when suite was last updated */
  updated_at: string;
}

/**
 * Wrapper for YAML serialization
 */
export interface TestSuiteData {
  test_suite: TestSuiteDefinition;
}

/**
 * Result from a single metric evaluation
 */
export interface MetricResult {
  /** Type of metric */
  type: MetricType;
  /** Metric score (0.0 to 1.0) */
  score: number;
  /** Whether metric passed threshold */
  passed: boolean;
  /** Threshold that was used */
  threshold: number;
  /** Explanation from DeepEval */
  reason?: string | null;
  /** Error if metric failed to execute */
  error?: string | null;
}

/**
 * Execution result for a single unit test
 */
export interface UnitTestExecutionResult {
  /** Name of the test */
  test_name: string;
  /** Reference to prompt file */
  prompt_reference: string;
  /** Template variables used */
  template_variables: Record<string, unknown>;
  /** Output from prompt execution */
  actual_output: string;
  /** Expected output for comparison */
  expected_output?: string | null;
  /** Results from all metrics */
  metric_results: MetricResult[];
  /** Whether all metrics passed */
  overall_passed: boolean;
  /** Execution duration in milliseconds */
  execution_time_ms: number;
  /** ISO timestamp when test was executed */
  executed_at: string;
  /** Error if test failed to execute */
  error?: string | null;
}

/**
 * Execution result for entire test suite
 */
export interface TestSuiteExecutionResult {
  /** Name of the suite */
  suite_name: string;
  /** Results from each test */
  test_results: UnitTestExecutionResult[];
  /** Total number of tests executed */
  total_tests: number;
  /** Number of tests that passed */
  passed_tests: number;
  /** Number of tests that failed */
  failed_tests: number;
  /** Total execution time in milliseconds */
  total_execution_time_ms: number;
  /** ISO timestamp when suite was executed */
  executed_at: string;
}

/**
 * Wrapper for execution YAML serialization
 */
export interface TestSuiteExecutionData {
  execution: TestSuiteExecutionResult;
}

/**
 * Summary of test suite for listing
 */
export interface TestSuiteSummary {
  /** Suite name */
  name: string;
  /** Suite description */
  description: string;
  /** Number of tests in suite */
  test_count: number;
  /** Tags for organization */
  tags: string[];
  /** File path to suite definition */
  file_path: string;
  /** ISO timestamp of last execution */
  last_execution?: string | null;
  /** Whether last execution passed */
  last_execution_passed?: boolean | null;
}