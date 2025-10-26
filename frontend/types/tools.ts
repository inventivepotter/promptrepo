/**
 * Tool Types
 * Matches backend models from backend/services/tool/models.py
 */

// Re-export types from generated API types to maintain backward compatibility
import type { components } from './generated/api';

export type ParameterSchema = components['schemas']['ParameterSchema'];
export type ParametersDefinition = components['schemas']['ParametersDefinition-Output'];
export type MockConfig = components['schemas']['MockConfig'];
export type ToolMetadata = components['schemas']['ToolMetadata'];
export type ToolDefinition = components['schemas']['ToolDefinition'];
export type ToolSummary = components['schemas']['ToolSummary'];
export type ToolSaveResponse = components['schemas']['ToolSaveResponse'];
export type ToolParameterType = components['schemas']['ToolParameterType'];

// Form state for tool editor
export interface ToolFormState {
  name: string;
  description: string;
  parameters: ParametersDefinition;
  mockEnabled: boolean;
  mockResponse: string;
  version: string;
  author: string;
  tags: string[];
}

// Parameter form state for individual parameter editing
export interface ParameterFormState {
  name: string;
  type: ToolParameterType;
  description: string;
  required: boolean;
  enumValues?: string[];
  defaultValue?: unknown;
}

// Request/Response types for API calls
export interface CreateToolRequest {
  repo_name: string;
  tool: ToolDefinition;
}

export interface ValidateToolResponse {
  valid: boolean;
  errors?: string[];
}