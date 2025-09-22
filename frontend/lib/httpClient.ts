import { HttpMethod, RequestConfig } from '@/types/ApiResponse';
import { getAuthHeaders } from '../utils/authHeaders';
import {
  OpenApiResponse,
  StandardResponse,
  ErrorResponse,
  ResponseStatus
} from '@/types/OpenApiResponse';

interface HttpClientConfig {
  baseUrl?: string;
  port?: number;
  defaultHeaders?: Record<string, string>;
  timeout?: number;
}

class HttpClient {
  private baseUrl: string;
  private defaultHeaders: Record<string, string>;
  private timeout: number;

  constructor(config: HttpClientConfig = {}) {
    // Use direct backend calls instead of proxy for non-public endpoints
    this.baseUrl = config.baseUrl || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3000';
    
    // Add port if specified
    if (config.port && !this.baseUrl.includes(':')) {
      this.baseUrl = `${this.baseUrl}:${config.port}`;
    }

    this.defaultHeaders = {
      'Content-Type': 'application/json',
      ...config.defaultHeaders
    };
    
    this.timeout = config.timeout || 180000; // 180 seconds (3 minutes) default
  }

  // Middleware to automatically inject auth token for backend calls only
  private injectAuthTokenForBackendCalls(
    url: string,
    headers: Record<string, string>
  ): Record<string, string> {
    // Only inject auth for backend API calls (not proxy calls or external requests)
    const isBackendCall = url.includes(this.baseUrl) && url.includes('/api/');
    
    if (!isBackendCall) {
      return headers;
    }

    // Get auth headers from utility
    const authHeaders = getAuthHeaders();
    
    return {
      ...headers,
      ...authHeaders
    };
  }

  private async makeRequest<T>(
    endpoint: string,
    method: HttpMethod,
    data?: unknown,
    config?: RequestConfig
  ): Promise<OpenApiResponse<T>> {
    try {
      // Ensure endpoint has /api prefix for backend calls
      const normalizedEndpoint = endpoint.startsWith('/api/') ? endpoint : `/api${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
      const url = `${this.baseUrl}${normalizedEndpoint}`;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      // Merge headers and inject auth token for backend calls only
      const mergedHeaders = {
        ...this.defaultHeaders,
        ...config?.headers
      };
      
      const headersWithAuth = this.injectAuthTokenForBackendCalls(url, mergedHeaders);

      const requestConfig: RequestInit = {
        method,
        headers: headersWithAuth,
        signal: config?.signal || controller.signal,
      };

      if (data && method !== HttpMethod.GET) {
        requestConfig.body = JSON.stringify(data);
      }

      const response = await fetch(url, requestConfig);
      clearTimeout(timeoutId);
      
      const statusCode = response.status;

      let responseData: unknown;
      
      try {
        responseData = await response.json();
      } catch {
        // If response is not JSON, create an error response in OpenAPI format
        const errorResponse: ErrorResponse = {
          status: ResponseStatus.ERROR,
          type: `/errors/http-${response.status}`,
          title: response.statusText || 'Request Failed',
          detail: `HTTP ${response.status}: ${response.statusText}`,
          meta: {
            timestamp: new Date().toISOString(),
            request_id: config?.headers?.['X-Request-ID'],
            correlation_id: config?.headers?.['X-Correlation-ID']
          }
        };
        return errorResponse;
      }

      // Check if the response is already in OpenAPI format by checking for required fields
      const apiResponse = responseData as Record<string, unknown>;
      const hasOpenApiFormat = apiResponse?.status && apiResponse?.meta;
      
      if (hasOpenApiFormat) {
        // Response is already in OpenAPI format, return as-is
        return responseData as OpenApiResponse<T>;
      }
      
      // Convert legacy format to OpenAPI format for consistency
      if (response.ok) {
        const standardResponse: StandardResponse<T> = {
          status: ResponseStatus.SUCCESS,
          data: responseData as T,
          message: apiResponse?.message as string | undefined,
          meta: {
            timestamp: new Date().toISOString(),
            request_id: config?.headers?.['X-Request-ID'],
            correlation_id: config?.headers?.['X-Correlation-ID']
          }
        };
        return standardResponse;
      } else {
        // Convert to error response
        const errorResponse: ErrorResponse = {
          status: ResponseStatus.ERROR,
          type: `/errors/http-${response.status}`,
          title: apiResponse?.title as string || 'Request Failed',
          detail: apiResponse?.detail as string || apiResponse?.error as string || `HTTP ${response.status}`,
          meta: {
            timestamp: new Date().toISOString(),
            request_id: config?.headers?.['X-Request-ID'],
            correlation_id: config?.headers?.['X-Correlation-ID']
          }
        };
        return errorResponse;
      }
    } catch (error) {
      // Handle AbortError specifically
      if (error instanceof Error && error.name === 'AbortError') {
        const timeoutError: ErrorResponse = {
          status: ResponseStatus.ERROR,
          type: '/errors/timeout',
          title: 'Request Timeout',
          detail: 'The request timed out. Please try again.',
          meta: {
            timestamp: new Date().toISOString(),
            request_id: config?.headers?.['X-Request-ID'],
            correlation_id: config?.headers?.['X-Correlation-ID']
          }
        };
        return timeoutError;
      }
      
      // Handle all other errors with proper error handling
      const errorMessage = error instanceof Error ? error.message :
                          (error ? String(error) : 'Unknown error occurred');

      const networkError: ErrorResponse = {
        status: ResponseStatus.ERROR,
        type: '/errors/network',
        title: 'Network Error',
        detail: errorMessage,
        meta: {
          timestamp: new Date().toISOString(),
          request_id: config?.headers?.['X-Request-ID'],
          correlation_id: config?.headers?.['X-Correlation-ID']
        }
      };
      return networkError;
    }
  }

  // GET request
  async get<T>(endpoint: string, config?: RequestConfig): Promise<OpenApiResponse<T>> {
    return this.makeRequest<T>(endpoint, HttpMethod.GET, undefined, config);
  }

  // POST request
  async post<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<OpenApiResponse<T>> {
    return this.makeRequest<T>(endpoint, HttpMethod.POST, data, config);
  }

  // PUT request
  async put<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<OpenApiResponse<T>> {
    return this.makeRequest<T>(endpoint, HttpMethod.PUT, data, config);
  }

  // PATCH request
  async patch<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<OpenApiResponse<T>> {
    return this.makeRequest<T>(endpoint, HttpMethod.PATCH, data, config);
  }

  // DELETE request
  async delete<T>(endpoint: string, config?: RequestConfig): Promise<OpenApiResponse<T>> {
    return this.makeRequest<T>(endpoint, HttpMethod.DELETE, undefined, config);
  }

  // Update base configuration
  updateConfig(config: Partial<HttpClientConfig>) {
    if (config.baseUrl) {
      this.baseUrl = config.baseUrl;
    }
    if (config.port && !this.baseUrl.includes(':')) {
      this.baseUrl = `${this.baseUrl}:${config.port}`;
    }
    if (config.defaultHeaders) {
      this.defaultHeaders = { ...this.defaultHeaders, ...config.defaultHeaders };
    }
    if (config.timeout) {
      this.timeout = config.timeout;
    }
  }

  // Set authorization header
  setAuthToken(token: string) {
    this.defaultHeaders['Authorization'] = `Bearer ${token}`;
  }

  // Remove authorization header
  clearAuthToken() {
    delete this.defaultHeaders['Authorization'];
  }
}

// Create and export a singleton instance
const httpClient = new HttpClient();

export default httpClient;

// Also export the class for custom instances if needed
export { HttpClient };