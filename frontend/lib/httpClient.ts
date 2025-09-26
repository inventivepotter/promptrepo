import {
  OpenApiResponse,
  StandardResponse,
  ErrorResponse,
  ResponseStatus
} from '@/types/OpenApiResponse';

// HTTP method enum
export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  PATCH = 'PATCH',
  DELETE = 'DELETE'
}

// Request configuration interface
export interface RequestConfig {
  headers?: Record<string, string>;
  signal?: AbortSignal;
}

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
    // Use Next.js API proxy to ensure cookies are properly forwarded
    this.baseUrl = config.baseUrl || 'http://localhost:3000';
    
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

  // Middleware to ensure credentials are included for API calls (httpOnly cookies)
  private injectAuthTokenForApiCalls(
    url: string,
    headers: Record<string, string>
  ): Record<string, string> {
    // All API calls should include credentials for cookie forwarding
    const isApiCall = url.includes('/api/v0');
    
    if (!isApiCall) {
      return headers;
    }

    // With httpOnly cookies, we don't need to manually inject auth headers
    // The browser automatically sends cookies with requests to same origin
    // Just return the headers as-is
    return headers;
  }

  private async makeRequest<T>(
    endpoint: string,
    method: HttpMethod,
    data?: unknown,
    config?: RequestConfig
  ): Promise<OpenApiResponse<T>> {
    try {
      // Ensure endpoint has /api prefix and goes through Next.js proxy
      const normalizedEndpoint = endpoint.startsWith('/api/v0') ? endpoint : `/api${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
      const url = `${this.baseUrl}${normalizedEndpoint}`;
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      // Merge headers and ensure credentials are included for cookie forwarding
      const mergedHeaders = {
        ...this.defaultHeaders,
        ...config?.headers
      };
      
      const headersWithAuth = this.injectAuthTokenForApiCalls(url, mergedHeaders);

      const requestConfig: RequestInit = {
        method,
        headers: headersWithAuth,
        credentials: 'include', // Include cookies for httpOnly authentication
        signal: config?.signal || controller.signal,
      };

      if (data && method !== HttpMethod.GET) {
        requestConfig.body = JSON.stringify(data);
      }

      const response = await fetch(url, requestConfig);
      clearTimeout(timeoutId);

      let responseData: unknown;
      
      try {
        responseData = await response.json();
      } catch {
        // If response is not JSON, create an error response in OpenAPI format
        const errorResponse: ErrorResponse = {
          status: ResponseStatus.ERROR,
          status_code: response.status,
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
      
      return responseData as OpenApiResponse<T>;
    } catch (error) {
      // Handle AbortError specifically
      if (error instanceof Error && error.name === 'AbortError') {
        const timeoutError: ErrorResponse = {
          status: ResponseStatus.ERROR,
          status_code: 408, // HTTP 408 Request Timeout
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
        status_code: 500, // Network error, no HTTP status
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