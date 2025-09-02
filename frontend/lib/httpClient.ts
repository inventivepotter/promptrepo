import { ApiResponse, ApiResult, HttpMethod, RequestConfig } from '@/types/ApiResponse';
import { getAuthHeaders } from '../utils/authHeaders';

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
  ): Promise<ApiResult<T>> {
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

      let responseData: ApiResponse<T>;
      
      try {
        responseData = await response.json();
      } catch {
        // If response is not JSON, create a structured response
        responseData = {
          success: response.ok,
          data: response.ok ? ({} as T) : undefined,
          error: response.ok ? undefined : `HTTP ${response.status}: ${response.statusText}`,
          message: response.statusText
        };
      }

      if (response.ok && responseData.success !== false) {
        return {
          success: true,
          data: responseData.data || responseData as T,
          message: responseData.message
        };
      } else {
        return {
          success: false,
          error: responseData.error || `HTTP ${response.status}: ${response.statusText}`,
          message: responseData.message || response.statusText,
          statusCode: response.status
        };
      }
    } catch (error) {
      // Handle AbortError specifically
      if (error instanceof Error && error.name === 'AbortError') {
        return {
          success: false,
          error: 'Request timeout',
          message: 'The request timed out. Please try again.',
          statusCode: 408
        };
      }
      
      // Handle all other errors with proper error handling
      const errorMessage = error instanceof Error ? error.message :
                          (error ? String(error) : 'Unknown error occurred');

      return {
        success: false,
        error: errorMessage,
        message: 'Network error occurred. Please check your connection.',
        statusCode: 0
      };
    }
  }

  // GET request
  async get<T>(endpoint: string, config?: RequestConfig): Promise<ApiResult<T>> {
    return this.makeRequest<T>(endpoint, HttpMethod.GET, undefined, config);
  }

  // POST request
  async post<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<ApiResult<T>> {
    return this.makeRequest<T>(endpoint, HttpMethod.POST, data, config);
  }

  // PUT request
  async put<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<ApiResult<T>> {
    return this.makeRequest<T>(endpoint, HttpMethod.PUT, data, config);
  }

  // PATCH request
  async patch<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<ApiResult<T>> {
    return this.makeRequest<T>(endpoint, HttpMethod.PATCH, data, config);
  }

  // DELETE request
  async delete<T>(endpoint: string, config?: RequestConfig): Promise<ApiResult<T>> {
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