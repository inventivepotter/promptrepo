/**
 * Tool Types
 * Matches backend models from backend/services/tool/models.py
 */

// Re-export types from generated API types to maintain backward compatibility
import type { components } from './generated/api';

export type ParameterSchema = components['schemas']['ParameterSchema'];
export type ParametersDefinition = components['schemas']['ParametersDefinition-Output'];
export type ReturnsSchema = components['schemas']['ReturnsSchema-Output'];
export type MockConfig = components['schemas']['MockConfig'];
export type ContentType = components['schemas']['ContentType'];
export type MockType = components['schemas']['MockType'];
export type ToolDefinition = components['schemas']['ToolDefinition-Output'];
export type ToolMeta = components['schemas']['ToolMeta'];
export type ToolData = components['schemas']['ToolData-Output'];
export type ToolDataInput = components['schemas']['ToolData-Input'];
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
  enumValues?: unknown[];
  defaultValue?: unknown;
}

// Validation response
export interface ValidateToolResponse {
  valid: boolean;
  errors?: string[];
}