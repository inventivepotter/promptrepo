/**
 * Utility functions for working with OpenAPI responses
 */

import {
  OpenApiResponse,
  StandardResponse,
  ErrorResponse,
  PaginatedResponse,
  isStandardResponse,
  isErrorResponse,
  isPaginatedResponse,
  ResponseStatus,
  ErrorDetail
} from '@/types/OpenApiResponse';

/**
 * Check if a response is successful
 */
export function isSuccess<T>(response: OpenApiResponse<T>): boolean {
  return response.status === ResponseStatus.SUCCESS;
}

/**
 * Check if a response is an error
 */
export function isError<T>(response: OpenApiResponse<T>): boolean {
  return response.status === ResponseStatus.ERROR;
}

/**
 * Extract data from a response or throw an error
 */
export function unwrapOrThrow<T>(response: OpenApiResponse<T>): T {
  if (isErrorResponse(response)) {
    throw new Error(response.detail || response.title);
  }

  if (isPaginatedResponse(response)) {
    return response.data as T;
  }

  if (isStandardResponse(response)) {
    if (response.data === undefined) {
      throw new Error('No data in response');
    }
    return response.data;
  }

  throw new Error('Unknown response format');
}

/**
 * Extract data from a response or return a default value
 */
export function unwrapOrDefault<T>(response: OpenApiResponse<T>, defaultValue: T): T {
  try {
    return unwrapOrThrow(response);
  } catch {
    return defaultValue;
  }
}

/**
 * Extract error message from an error response
 */
export function getErrorMessage(response: OpenApiResponse<unknown>): string | null {
  if (!isErrorResponse(response)) {
    return null;
  }

  // Try to get the most specific error message
  if (response.detail) {
    return response.detail;
  }

  if (response.errors && response.errors.length > 0) {
    return response.errors.map(e => e.message).join(', ');
  }

  return response.title || 'An error occurred';
}

/**
 * Extract error details from an error response
 */
export function getErrorDetails(response: OpenApiResponse<unknown>): ErrorDetail[] | null {
  if (!isErrorResponse(response)) {
    return null;
  }

  return response.errors || null;
}

/**
 * Get pagination info from a paginated response
 */
export function getPaginationInfo<T>(response: OpenApiResponse<T>) {
  if (!isPaginatedResponse(response)) {
    return null;
  }

  return response.pagination;
}

/**
 * Create a successful standard response
 */
export function createSuccessResponse<T>(data: T, message?: string): StandardResponse<T> {
  return {
    status: ResponseStatus.SUCCESS,
    data,
    message,
    meta: {
      timestamp: new Date().toISOString()
    }
  };
}

/**
 * Create an error response
 */
export function createErrorResponse(
  title: string,
  detail?: string,
  type: string = '/errors/client-error'
): ErrorResponse {
  return {
    status: ResponseStatus.ERROR,
    type,
    title,
    detail,
    meta: {
      timestamp: new Date().toISOString()
    }
  };
}

/**
 * Transform a response by mapping the data
 */
export function mapResponseData<T, U>(
  response: OpenApiResponse<T>,
  mapper: (data: T) => U
): OpenApiResponse<U> {
  if (isStandardResponse(response)) {
    return {
      ...response,
      data: response.data ? mapper(response.data) : undefined
    } as StandardResponse<U>;
  }

  if (isPaginatedResponse(response)) {
    return {
      ...response,
      data: response.data.map(item => mapper(item as T))
    } as PaginatedResponse<U>;
  }

  // Error response, return as-is
  return response as ErrorResponse;
}

/**
 * Chain multiple API calls with proper error handling
 */
export async function chainApiCalls<T>(
  calls: Array<() => Promise<OpenApiResponse<unknown>>>,
  onError?: (error: ErrorResponse, index: number) => void
): Promise<T[]> {
  const results: T[] = [];

  for (let i = 0; i < calls.length; i++) {
    const response = await calls[i]();

    if (isError(response)) {
      if (onError) {
        onError(response as ErrorResponse, i);
      }
      throw new Error(getErrorMessage(response) || 'API call failed');
    }

    results.push(unwrapOrThrow(response) as T);
  }

  return results;
}

/**
 * Retry an API call with exponential backoff
 */
export async function retryApiCall<T>(
  apiCall: () => Promise<OpenApiResponse<T>>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<OpenApiResponse<T>> {
  let lastError: ErrorResponse | null = null;

  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const response = await apiCall();

    if (isSuccess(response)) {
      return response;
    }

    lastError = response as ErrorResponse;

    if (attempt < maxRetries - 1) {
      // Exponential backoff
      const delay = baseDelay * Math.pow(2, attempt);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  return lastError || createErrorResponse('Max retries exceeded');
}

/**
 * Batch multiple API calls and wait for all to complete
 */
export async function batchApiCalls<T extends Record<string, () => Promise<OpenApiResponse<unknown>>>>(
  calls: T
): Promise<{ [K in keyof T]: OpenApiResponse<unknown> }> {
  const entries = Object.entries(calls);
  const results = await Promise.all(entries.map(([_, call]) => call()));

  return Object.fromEntries(
    entries.map(([key], index) => [key, results[index]])
  ) as { [K in keyof T]: OpenApiResponse<unknown> };
}

/**
 * Helper to handle API response in React components
 */
export function handleApiResponse<T>(
  response: OpenApiResponse<T>,
  options: {
    onSuccess?: (data: T) => void;
    onError?: (error: string) => void;
    throwOnError?: boolean;
  } = {}
): T | null {
  if (isSuccess(response)) {
    const data = unwrapOrThrow(response);
    options.onSuccess?.(data);
    return data;
  }

  const errorMessage = getErrorMessage(response) || 'Request failed';
  options.onError?.(errorMessage);

  if (options.throwOnError) {
    throw new Error(errorMessage);
  }

  return null;
}