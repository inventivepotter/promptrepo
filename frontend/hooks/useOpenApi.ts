/**
 * React hooks for API calls with OpenAPI responses
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { 
  OpenApiResponse, 
  StandardResponse, 
  ErrorResponse, 
  PaginatedResponse,
  isStandardResponse,
  isErrorResponse,
  ResponseStatus
} from '@/types/OpenApiResponse';
import { 
  isSuccess, 
  getErrorMessage,
  unwrapOrThrow 
} from '@/lib/openApiUtils';

/**
 * State for API calls
 */
export interface ApiState<T> {
  data?: T;
  error?: string;
  isLoading: boolean;
  isSuccess: boolean;
  isError: boolean;
}

/**
 * Options for useOpenApi hook
 */
export interface UseOpenApiOptions {
  immediate?: boolean;
  onSuccess?: (data: unknown) => void;
  onError?: (error: string) => void;
  retries?: number;
  retryDelay?: number;
}

/**
 * Hook for making API calls with OpenAPI responses
 */
export function useOpenApi<T>(
  apiCall: () => Promise<OpenApiResponse<T>>,
  options: UseOpenApiOptions = {}
) {
  const [state, setState] = useState<ApiState<T>>({
    isLoading: false,
    isSuccess: false,
    isError: false
  });

  const isMountedRef = useRef(true);
  const abortControllerRef = useRef<AbortController | undefined>(undefined);

  const execute = useCallback(async () => {
    // Cancel any pending requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    setState({ isLoading: true, isSuccess: false, isError: false });

    let attempts = 0;
    const maxAttempts = (options.retries || 0) + 1;
    const retryDelay = options.retryDelay || 1000;

    while (attempts < maxAttempts) {
      try {
        const response = await apiCall();

        if (!isMountedRef.current) return;

        if (isSuccess(response)) {
          const data = unwrapOrThrow(response);
          setState({
            data,
            isLoading: false,
            isSuccess: true,
            isError: false
          });
          options.onSuccess?.(data);
          return;
        } else {
          const errorMessage = getErrorMessage(response) || 'Request failed';
          
          if (attempts === maxAttempts - 1) {
            // Last attempt failed
            setState({
              error: errorMessage,
              isLoading: false,
              isSuccess: false,
              isError: true
            });
            options.onError?.(errorMessage);
            return;
          }
        }
      } catch (error) {
        if (!isMountedRef.current) return;

        const errorMessage = error instanceof Error ? error.message : 'An error occurred';
        
        if (attempts === maxAttempts - 1) {
          // Last attempt failed
          setState({
            error: errorMessage,
            isLoading: false,
            isSuccess: false,
            isError: true
          });
          options.onError?.(errorMessage);
          return;
        }
      }

      // Wait before retry
      attempts++;
      if (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, retryDelay * attempts));
      }
    }
  }, [apiCall, options]);

  const reset = useCallback(() => {
    setState({
      isLoading: false,
      isSuccess: false,
      isError: false
    });
  }, []);

  // Execute immediately if requested
  useEffect(() => {
    if (options.immediate) {
      execute();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      abortControllerRef.current?.abort();
    };
  }, []);

  return { state, execute, reset };
}

/**
 * Hook for paginated API calls
 */
export function usePaginatedApi<T>(
  apiCall: (page: number, pageSize: number) => Promise<OpenApiResponse<T[]>>,
  pageSize: number = 10,
  options: UseOpenApiOptions = {}
) {
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);

  const { state, execute, reset } = useOpenApi(
    () => apiCall(page, pageSize),
    {
      ...options,
      onSuccess: (data) => {
        // Extract pagination info if available
        options.onSuccess?.(data);
      }
    }
  );

  const nextPage = useCallback(() => {
    if (hasNext) {
      setPage(p => p + 1);
    }
  }, [hasNext]);

  const previousPage = useCallback(() => {
    if (hasPrevious) {
      setPage(p => p - 1);
    }
  }, [hasPrevious]);

  const goToPage = useCallback((newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
    }
  }, [totalPages]);

  // Re-execute when page changes
  useEffect(() => {
    execute();
  }, [page, execute]);

  return {
    state,
    page,
    totalPages,
    hasNext,
    hasPrevious,
    nextPage,
    previousPage,
    goToPage,
    reset
  };
}

/**
 * Hook for making multiple API calls in parallel
 */
export function useMultiApi<T extends Record<string, () => Promise<OpenApiResponse<unknown>>>>(
  apiCalls: T,
  options: UseOpenApiOptions = {}
): {
  states: { [K in keyof T]: ApiState<unknown> };
  execute: () => Promise<void>;
  reset: () => void;
} {
  const [states, setStates] = useState<{ [K in keyof T]: ApiState<unknown> }>(
    () => Object.keys(apiCalls).reduce((acc, key) => ({
      ...acc,
      [key]: { isLoading: false, isSuccess: false, isError: false }
    }), {} as { [K in keyof T]: ApiState<unknown> })
  );

  const execute = useCallback(async () => {
    // Set all to loading
    setStates(prev => 
      Object.keys(prev).reduce((acc, key) => ({
        ...acc,
        [key]: { ...prev[key], isLoading: true, isSuccess: false, isError: false }
      }), {} as { [K in keyof T]: ApiState<unknown> })
    );

    // Execute all calls in parallel
    const results = await Promise.allSettled(
      Object.entries(apiCalls).map(async ([key, apiCall]) => {
        try {
          const response = await apiCall();
          return { key, response };
        } catch (error) {
          return { key, error };
        }
      })
    );

    // Update states based on results
    const newStates = { ...states };
    
    results.forEach((result) => {
      if (result.status === 'fulfilled') {
        const { key, response, error } = result.value as { key: string; response?: OpenApiResponse<unknown>; error?: unknown };
        
        if (response && isSuccess(response)) {
          newStates[key as keyof T] = {
            data: unwrapOrThrow(response),
            isLoading: false,
            isSuccess: true,
            isError: false
          };
        } else if (response) {
          newStates[key as keyof T] = {
            error: getErrorMessage(response) || 'Request failed',
            isLoading: false,
            isSuccess: false,
            isError: true
          };
        } else if (error) {
          newStates[key as keyof T] = {
            error: error instanceof Error ? error.message : 'Request failed',
            isLoading: false,
            isSuccess: false,
            isError: true
          };
        }
      } else {
        // Promise rejected
        const error = result.reason;
        // Find which key this error belongs to
        Object.keys(apiCalls).forEach(key => {
          if (!newStates[key as keyof T].isSuccess) {
            newStates[key as keyof T] = {
              error: error instanceof Error ? error.message : 'Request failed',
              isLoading: false,
              isSuccess: false,
              isError: true
            };
          }
        });
      }
    });

    setStates(newStates);
    
    // Call callbacks
    const hasErrors = Object.values(newStates).some(s => s.isError);
    const allSuccess = Object.values(newStates).every(s => s.isSuccess);
    
    if (allSuccess) {
      options.onSuccess?.(newStates);
    } else if (hasErrors) {
      const errors = Object.entries(newStates)
        .filter(([_, state]) => state.isError)
        .map(([key, state]) => `${key}: ${state.error}`)
        .join(', ');
      options.onError?.(errors);
    }
  }, [apiCalls, options, states]);

  const reset = useCallback(() => {
    setStates(
      Object.keys(apiCalls).reduce((acc, key) => ({
        ...acc,
        [key]: { isLoading: false, isSuccess: false, isError: false }
      }), {} as { [K in keyof T]: ApiState<unknown> })
    );
  }, [apiCalls]);

  // Execute immediately if requested
  useEffect(() => {
    if (options.immediate) {
      execute();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return { states, execute, reset };
}

/**
 * Hook for mutations (POST, PUT, PATCH, DELETE)
 */
export function useMutation<TData, TVariables>(
  mutation: (variables: TVariables) => Promise<OpenApiResponse<TData>>,
  options: UseOpenApiOptions = {}
) {
  const [state, setState] = useState<ApiState<TData>>({
    isLoading: false,
    isSuccess: false,
    isError: false
  });

  const mutate = useCallback(async (variables: TVariables) => {
    setState({ isLoading: true, isSuccess: false, isError: false });

    try {
      const response = await mutation(variables);

      if (isSuccess(response)) {
        const data = unwrapOrThrow(response);
        setState({
          data,
          isLoading: false,
          isSuccess: true,
          isError: false
        });
        options.onSuccess?.(data);
        return data;
      } else {
        const errorMessage = getErrorMessage(response) || 'Mutation failed';
        setState({
          error: errorMessage,
          isLoading: false,
          isSuccess: false,
          isError: true
        });
        options.onError?.(errorMessage);
        throw new Error(errorMessage);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Mutation failed';
      setState({
        error: errorMessage,
        isLoading: false,
        isSuccess: false,
        isError: true
      });
      options.onError?.(errorMessage);
      throw error;
    }
  }, [mutation, options]);

  const reset = useCallback(() => {
    setState({
      isLoading: false,
      isSuccess: false,
      isError: false
    });
  }, []);

  return { state, mutate, reset };
}