/**
 * TypeScript types for DeepEval Eval Framework
 * Re-exports types from generated API and adds additional helper types
 */

import type { components } from '@/types/generated/api';

// Re-export generated types from OpenAPI schema
export type MetricConfig = components['schemas']['MetricConfig'];
export type MetricResult = components['schemas']['MetricResult'];
export type EvalExecutionResult = components['schemas']['EvalExecutionResult'];
export type TestExecutionResult = components['schemas']['TestExecutionResult'];
export type EvalMeta = components['schemas']['EvalMeta'];
export type ExpectedTestFieldsModel = components['schemas']['ExpectedTestFieldsModel'];
export type ActualTestFieldsModel = components['schemas']['ActualTestFieldsModel'];
export type EvalDefinition = components['schemas']['EvalDefinition-Output'];
export type EvalData = components['schemas']['EvalData'];
export type TestDefinition = components['schemas']['TestDefinition-Output'];
export type MetricType = components['schemas']['MetricType'];

// Re-export MetricMetadataModel from generated types
export type MetricMetadata = components['schemas']['MetricMetadataModel'];

// EvalMeta is used as the summary type (API returns EvalMeta[])
export type EvalSummary = EvalMeta;

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

// ============================================================================
// CONVERSATIONAL TEST TYPES
// ============================================================================

/**
 * Role of a turn in a conversation
 */
export type TurnRole = 'user' | 'assistant';

/**
 * A single turn in a conversation
 */
export interface Turn {
  /** Role of the speaker */
  role: TurnRole;
  /** Content of the message */
  content: string;
  /** Retrieved context for this turn (for RAG evaluation) */
  retrieval_context?: string[];
  /** Tools called during this turn (for agent evaluation) */
  tools_called?: Record<string, unknown>[];
}

/**
 * Type of test - single turn or conversational
 */
export type TestType = 'single_turn' | 'conversational';

/**
 * Configuration for conversational test generation
 */
export interface ConversationalTestConfig {
  /** Goal for the simulated user */
  user_goal?: string;
  /** Persona description for the simulated user */
  user_persona?: string;
  /** Minimum number of conversation turns */
  min_turns?: number;
  /** Maximum number of conversation turns */
  max_turns?: number;
  /** When to stop the conversation */
  stopping_criteria?: string;
  /** Expected outcome of the conversation */
  expected_outcome?: string;
  /** Role description for the chatbot being tested */
  chatbot_role?: string;
}

/**
 * Request for simulating a conversation based on user goal
 */
export interface SimulateConversationRequest {
  repo_name: string;
  prompt_reference: string;
  user_goal: string;
  user_persona?: string;
  min_turns?: number;
  max_turns?: number;
  stopping_criteria?: string;
  template_variables?: Record<string, unknown>;
  /** LLM provider (uses prompt's config if not provided) */
  provider?: string;
  /** LLM model (uses prompt's config if not provided) */
  model?: string;
}

/**
 * Response from conversation simulation
 */
export interface SimulateConversationResponse {
  turns: Turn[];
  goal_achieved: boolean;
  stopping_reason?: string;
}

/**
 * Extended TestDefinition with conversational fields
 * This extends the generated type with our new fields
 */
export interface ConversationalTestDefinition extends Omit<TestDefinition, 'test_type' | 'turns' | 'conversational_config'> {
  /** Type of test - single_turn or conversational */
  test_type?: TestType;
  /** Conversation turns for conversational tests (manually defined) */
  turns?: Turn[];
  /** Configuration for conversational test generation */
  conversational_config?: ConversationalTestConfig;
}