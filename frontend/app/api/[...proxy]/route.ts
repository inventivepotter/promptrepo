import { NextRequest, NextResponse } from 'next/server';

// Get backend URL from environment or default
const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:8080';

// Define public endpoints that should be proxied (from auth_middleware.py)
const PUBLIC_ENDPOINTS = new Set([
  // Auth endpoints
  '/api/v0/auth/login/github',
  '/api/v0/auth/callback/github',
  '/api/v0/auth/verify',
  '/api/v0/auth/logout',
  '/api/v0/auth/refresh',
  // Public provider info (available providers without requiring auth)
  '/api/v0/llm/providers/available',
  // Public config endpoints
  '/api/v0/config',
  '/api/v0/config/hosting-type',
  // Frontend required endpoints
  '/api/v0/repos/available',
  '/api/v0/repos/configured',
  '/api/v0/llm/providers/configured',
  '/api/v0/prompts',
  '/api/v0/llm/chat/completions',
  '/api/v0/prompts/commit-push'
]);

// Define public endpoint prefixes that should be matched with startsWith
const PUBLIC_ENDPOINT_PREFIXES = [
  // TODO: Make sure to only allow prompts/:id here not other endpoints
  '/api/v0/prompts/',
  '/api/v0/llm/providers/models/'
];

function isPublicEndpoint(path: string): boolean {
  // Direct match
  if (PUBLIC_ENDPOINTS.has(path)) {
    return true;
  }
  
  // Check for prefix matches
  for (const prefix of PUBLIC_ENDPOINT_PREFIXES) {
    if (path.startsWith(prefix)) {
      return true;
    }
  }
    
  return false;
}

async function proxyRequest(
  request: NextRequest,
  params: Promise<{ proxy: string[] }>
): Promise<NextResponse> {
  try {
    const { proxy } = await params;
    const path = proxy.join('/');
    const fullPath = `/api/${path}`;
    
    // Check if this is a public endpoint that should be proxied
    if (!isPublicEndpoint(fullPath)) {
      return NextResponse.json(
        {
          success: false,
          error: 'Endpoint not available through proxy',
          message: 'This endpoint should be accessed directly from the backend service'
        },
        { status: 404 }
      );
    }
    
    // Construct the target URL - preserve the /api prefix for backend
    const targetUrl = `${BACKEND_URL}/api/${path}`;
    
    // Get search parameters from the original request
    const searchParams = request.nextUrl.searchParams.toString();
    const fullTargetUrl = searchParams ? `${targetUrl}?${searchParams}` : targetUrl;

    // Prepare headers for the backend request
    const headers = new Headers();
    
    // Copy relevant headers from the original request
    const relevantHeaders = [
      'authorization',
      'content-type',
      'accept',
      'user-agent'
    ];
    
    relevantHeaders.forEach(headerName => {
      const headerValue = request.headers.get(headerName);
      if (headerValue) {
        headers.set(headerName, headerValue);
      }
    });

    // Prepare the request configuration
    const requestConfig: RequestInit = {
      method: request.method,
      headers,
    };

    // Add body for non-GET requests
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      try {
        const body = await request.text();
        if (body) {
          requestConfig.body = body;
        }
      } catch (error) {
        console.error('Error reading request body:', error);
      }
    }

    // Make the request to the backend
    const response = await fetch(fullTargetUrl, requestConfig);
    
    // Get the response body
    const responseBody = await response.text();
    
    // Create response headers
    const responseHeaders = new Headers();
    
    // Copy relevant response headers
    const relevantResponseHeaders = [
      'content-type',
      'cache-control',
      'etag',
      'expires',
      'last-modified'
    ];
    
    relevantResponseHeaders.forEach(headerName => {
      const headerValue = response.headers.get(headerName);
      if (headerValue) {
        responseHeaders.set(headerName, headerValue);
      }
    });

    // Add CORS headers for frontend
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, PATCH, OPTIONS');
    responseHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    return new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });

  } catch (error) {
    console.error('Proxy request failed:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Proxy request failed',
        message: error instanceof Error ? error.message : 'Unknown error occurred'
      },
      { status: 500 }
    );
  }
}

// Handle all HTTP methods
export async function GET(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  return proxyRequest(request, context.params);
}

export async function POST(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  return proxyRequest(request, context.params);
}

export async function PUT(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  return proxyRequest(request, context.params);
}

export async function DELETE(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  return proxyRequest(request, context.params);
}

export async function PATCH(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  return proxyRequest(request, context.params);
}

export async function OPTIONS(request: NextRequest, context: { params: Promise<{ proxy: string[] }> }) {
  // Handle preflight CORS requests
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}