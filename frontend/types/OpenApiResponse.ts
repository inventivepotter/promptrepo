/**
 * OpenAPI Response Types
 * Matches the backend's standardized response format
 */

// Response status enum matching backend
export enum ResponseStatus {
  SUCCESS = 'success',
  ERROR = 'error',
  PARTIAL = 'partial'
}

// Response metadata
export interface ResponseMeta {
  timestamp: string;
  request_id?: string;
  version?: string;
  correlation_id?: string;
}

// Error detail structure
export interface ErrorDetail {
  code: string;
  message: string;
  field?: string;
  context?: Record<string, unknown>;
}

// Standard successful response wrapper
export interface StandardResponse<T = unknown> {
  status: ResponseStatus;
  status_code: number;
  data?: T;
  message?: string;
  meta: ResponseMeta;
}

// Error response following RFC 7807 Problem Details
export interface ErrorResponse {
  status: ResponseStatus;
  status_code: number;
  type: string;
  title: string;
  detail?: string;
  instance?: string;
  errors?: ErrorDetail[];
  meta: ResponseMeta;
}

// Pagination metadata
export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

// Paginated response
export interface PaginatedResponse<T = unknown> {
  status: ResponseStatus;
  status_code: number;
  data: T[];
  pagination: PaginationMeta;
  message?: string;
  meta: ResponseMeta;
}

// Union type for all possible API responses
export type OpenApiResponse<T = unknown> = StandardResponse<T> | ErrorResponse | PaginatedResponse<T>;

// Type guards for response type checking
export function isStandardResponse<T>(response: OpenApiResponse<T>): response is StandardResponse<T> {
  return 'data' in response && !('pagination' in response) && !('type' in response);
}

export function isErrorResponse<T>(response: OpenApiResponse<T>): response is ErrorResponse {
  return 'type' in response && 'title' in response;
}

export function isPaginatedResponse<T>(response: OpenApiResponse<T>): response is PaginatedResponse<T> {
  return 'pagination' in response && 'data' in response;
}

// Normalized response type for frontend consumption
export interface OpenAPIResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    message: string;
    code?: string;
    details?: ErrorDetail[];
  };
  pagination?: PaginationMeta;
  meta?: ResponseMeta;
}